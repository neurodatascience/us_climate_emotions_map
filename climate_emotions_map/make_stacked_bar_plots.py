import pandas as pd
import plotly.express as px

# TODO: Use relative import .data_loader
from data_loader import DATA_DICTIONARIES, SURVEY_DATA

available_threshold_dict = {"3+": ["1", "2"], "4+": ["1", "2", "3"]}

AGG_OUTCOME_LABEL = "agg"
NA_OUTCOME_LABEL = "NA"

THEME = "plotly_white"
LAYOUTS = {
    "margin": {"l": 30, "r": 30, "t": 30, "b": 20},
    "title": {  # figure title position properties, see https://plotly.com/python/reference/layout/#layout-title
        "yanchor": "bottom",
        "yref": "paper",
        # "pad": {"t": 10},
        "y": 1,
    },
    # NOTE: to debug the title layout, use the "plotly" theme to make the plot area visible
}


def load_opinions_df(state: str | None, stratify: bool) -> pd.DataFrame | None:
    """Return the opinions data for the whole sample, stratified by state, or stratified by party."""
    if state is None and not stratify:
        return SURVEY_DATA["opinions_wholesample.tsv"]
    if state is not None:
        return SURVEY_DATA["opinions_state.tsv"]
    if stratify:
        return SURVEY_DATA["opinions_party.tsv"]
    return None


def aggregate_outcome_subset(
    df: pd.DataFrame, agg_outcomes: list, strata_col: str = None
):
    """
    Aggregate a subset of outcomes into a single outcome.
    This is used only when the response data is thresholded at a specific endorsement level.
    """
    if strata_col is None:
        agg_percent = df[df["outcome"].isin(agg_outcomes)]["percentage"].sum()
        agg_df = pd.DataFrame([{"percentage": agg_percent}])
    else:
        agg_df = (
            df[df["outcome"].isin(agg_outcomes)]
            .groupby([strata_col])["percentage"]
            .sum()
        )
        agg_df = pd.DataFrame(agg_df).reset_index()

    agg_df["outcome"] = AGG_OUTCOME_LABEL
    agg_df["question"] = df["question"].unique()[0]
    agg_df["sub_question"] = df["sub_question"].unique()[0]

    # remove original individual outcomes
    df = df[~df["outcome"].isin(agg_outcomes)]

    # append aggregated outcome
    df = pd.concat([df, agg_df])

    return df


def fill_na_percentage(df: pd.DataFrame, strata_col: str = None):
    """
    Fill in the missing percentage values for the NA outcome.
    This is used only when the response data is thresholded at a specific endorsement level.
    """
    if strata_col is None:
        na_percent = 1 - df["percentage"].sum()
        na_df = pd.DataFrame([{"percentage": na_percent}])
    else:
        na_df = 1 - df.groupby([strata_col])["percentage"].sum()
        na_df = pd.DataFrame(na_df).reset_index()

    na_df["outcome"] = NA_OUTCOME_LABEL
    na_df["question"] = df["question"].unique()[0]
    na_df["sub_question"] = df["sub_question"].unique()[0]
    df = pd.concat([df, na_df])
    return df


# TODO:
# - Remove legend
# - Add text annotations for each outcome (?)
# - Update colours
def plot_bars(
    plot_df,
    x="percentage",
    y="question",
    color="outcome",
    title="opinions",
    round_values=True,
    sort_order="descending",
) -> px.bar:
    """Make a stacked bar plot of the opinions of the whole sample, split by state and party."""

    if round_values:
        plot_df[x] = plot_df[x].round(3) * 100

    # if isinstance(sort_values, dict):
    #    print(f"ordering by {sort_values}")
    #    fig = px.bar(plot_df, x=x, y=y, color=color, title=title, category_orders=sort_values, text_auto=True)

    if sort_order == "descending":
        print("sorting in descending order")
        plot_df = plot_df.sort_values(by="outcome", ascending=False)
    elif sort_order == "ascending":
        print("ordering by ascending order")
        plot_df = plot_df.sort_values(by="outcome", ascending=True)
    else:
        pass

    fig = px.bar(
        plot_df,
        x=x,
        y=y,
        color=color,
        title=title,
        text_auto=True,
        template=THEME,
    )
    fig.update_xaxes(
        showgrid=False,
        showline=False,
        zeroline=False,
        title=None,
        showticklabels=False,
    )
    fig.update_yaxes(showgrid=False, title=None)
    # TODO: Hide y axis tick label?
    fig.update_layout(
        margin=LAYOUTS["margin"], title=LAYOUTS["title"]
    )  # , yaxis_title=None, xaxis_title=None)
    # Add percentage sign to the bar text
    fig.update_traces(texttemplate="%{x}%")
    return fig


def get_subquestion_text(question: str, subquestion: str):
    """Get the full text for a subquestion."""
    dict_df = DATA_DICTIONARIES["subquestion_dictionary.tsv"]
    question_text = dict_df[
        (dict_df["question"] == question)
        & (dict_df["sub_question"] == subquestion)
    ]["full_text"]

    return question_text.values[0]


def run(
    question: str,
    subquestion: str,
    state: str | None = None,
    stratify: bool = False,
    threshold: str | None = None,
    binarize_threshold: bool = False,
) -> px.bar:
    """
    Make plots for a given question, subquestion, and state.
    Optionally stratify by party and/or categorize by a threshold.
    """

    df = load_opinions_df(state, stratify)

    assert (
        question in df["question"].unique()
    ), f"Question {question} not found in data."
    assert (
        subquestion in df[df["question"] == question]["sub_question"].unique()
    ), f"Subquestion {subquestion} not found in data."

    # Get the question and subquestion
    q_df = df[
        (df["question"] == question) & (df["sub_question"] == subquestion)
    ].copy()

    y = "question"

    # Check if looking for particular state
    if state:
        assert (
            state in q_df["state"].unique()
        ), f"State {state} not found in data."

        print(f"Filtering for state {state}.")
        q_df = q_df[q_df["state"] == state]

    if stratify:

        strata = "party"
        y = strata
        assert strata in q_df.columns, f"{strata} column not found in data."

        print("Stratifying by {strata}.")

    else:
        strata = None

    if threshold:
        assert (
            threshold in available_threshold_dict
        ), f"Threshold {threshold} not found in available thresholds."

        print(f"Thresholding at {threshold}.")

        if binarize_threshold:
            print(f"Binarizing threshold at {threshold}.")

            include_outcomes = [threshold]

        else:
            include_outcomes = [threshold] + available_threshold_dict[
                threshold
            ]

        print(f"include_outcomes: {include_outcomes}")
        q_df = q_df[q_df["outcome"].isin(include_outcomes)]

        if not binarize_threshold:
            # aggregate outcomes less than the threshold
            q_df = aggregate_outcome_subset(
                q_df, available_threshold_dict[threshold], strata
            )

            # fill in the missing percentage values as the NA outcome
            q_df = fill_na_percentage(q_df, strata)

            cat_order = {
                "outcome": [threshold, NA_OUTCOME_LABEL, AGG_OUTCOME_LABEL]
            }

        else:
            # fill in the missing percentage values as the NA outcome
            q_df = fill_na_percentage(q_df, strata)
            cat_order = {"outcome": [threshold, NA_OUTCOME_LABEL]}

        q_df["outcome"] = pd.Categorical(q_df["outcome"], cat_order["outcome"])
        q_df = q_df.sort_values(by="outcome")

        sort_order = "predetermined"

    else:
        # exclude categorical thresholds
        q_df = q_df[~q_df["outcome"].isin(available_threshold_dict.keys())]
        sort_order = "descending"

    print(f"possible_outcomes: {q_df['outcome'].unique()}")

    stacked_bar = plot_bars(
        q_df,
        x="percentage",
        y=y,
        title=get_subquestion_text(question, subquestion),
        round_values=True,
        sort_order=sort_order,
    )
    return stacked_bar


if __name__ == "__main__":
    # Example run
    fig = run(
        question="q2",
        subquestion="1",
        state=None,
        stratify=True,
        threshold="3+",
        binarize_threshold=True,
    )
    fig.show()
