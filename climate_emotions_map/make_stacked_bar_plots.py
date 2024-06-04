import pandas as pd
import plotly.express as px

# from .data_loader import DATA_DICTIONARIES, SURVEY_DATA

# -------------------------------------------------------
# data paths
data_dir = "../data/"

opinions_whole_tsv = "opinions_wholesample.tsv"
opinions_state_tsv = "opinions_state.tsv"
opinions_party_tsv = "opinions_party.tsv"

subquestion_dict_tsv = "subquestion_dictionary.tsv"
outcome_dict = "outcome_dictionary.tsv"

opinions_whole_df = pd.read_csv(
    f"{data_dir}/survey_results/{opinions_whole_tsv}", sep="\t"
)
opinions_state_df = pd.read_csv(
    f"{data_dir}/survey_results/{opinions_state_tsv}", sep="\t"
)
opinions_party_df = pd.read_csv(
    f"{data_dir}/survey_results/{opinions_party_tsv}", sep="\t"
)

subquestion_dict_df = pd.read_csv(
    f"{data_dir}/data_dictionaries/{subquestion_dict_tsv}", sep="\t"
)
outcome_dict_df = pd.read_csv(
    f"{data_dir}/data_dictionaries/{outcome_dict}", sep="\t"
)
# -------------------------------------------------------

# Figure parameters
fig_kw = {
    "fontsize": 10,
    "width": 1200,
    "height": 500,
    "marker_line_width": 1,
    "marker_line_color": "black",
}


# Custom palettes
cool_warm_default = [
    "#f94144",
    "#f3722c",
    "#f8961e",
    "#f9844a",
    "#f9c74f",
    "#90be6d",
    "#43aa8b",
    "#4d908e",
    "#577590",
    "#277da1",
]

cool_warm_5 = ["#f94144", "#f3722c", "#f8961e", "#43aa8b", "#577590"]
cool_warm_7 = [
    "#f94144",
    "#f3722c",
    "#f8961e",
    "#90be6d",
    "#43aa8b",
    "#4d908e",
    "#577590",
]

binary_palette = ["#f8961e", "#43aa8b"]
ternary_palette = ["#f8961e", "#d5bdaf", "#43aa8b"]


# Global labels
agg_outcome_label = "other"
na_outcome_label = "NA"

# Pre-defined thresholds
available_threshold_dict = {"3+": ["1", "2"], "4+": ["1", "2", "3"]}


def load_df(state, stratify):
    if state is None and not stratify:
        return opinions_whole_df
    elif state is not None:
        return opinions_state_df
    elif stratify:
        return opinions_party_df
    else:
        return None


def aggregate_outcome_subset(df, agg_outcomes, stata_col=None):
    """aggregate a subset of outcomes into a single outcome. This is used only with thresholding."""
    if stata_col is None:
        agg_percent = df[df["outcome"].isin(agg_outcomes)]["percentage"].sum()
        agg_df = pd.DataFrame([{"percentage": agg_percent}])
    else:
        agg_df = (
            df[df["outcome"].isin(agg_outcomes)]
            .groupby([stata_col])["percentage"]
            .sum()
        )
        agg_df = pd.DataFrame(agg_df).reset_index()

    agg_df["outcome"] = agg_outcome_label
    agg_df["question"] = df["question"].unique()[0]
    agg_df["sub_question"] = df["sub_question"].unique()[0]

    # remove original individual outcomes
    df = df[~df["outcome"].isin(agg_outcomes)]

    # append aggregated outcome
    df = pd.concat([df, agg_df])

    return df


def fill_na_percentage(df, stata_col=None):
    """Fill in the missing percentage values for the NA outcome. This is used only with thresholding."""
    if stata_col is None:
        na_percent = 1 - df["percentage"].sum()
        na_df = pd.DataFrame([{"percentage": na_percent}])
    else:
        na_df = 1 - df.groupby([stata_col])["percentage"].sum()
        na_df = pd.DataFrame(na_df).reset_index()

    na_df["outcome"] = na_outcome_label
    na_df["question"] = df["question"].unique()[0]
    na_df["sub_question"] = df["sub_question"].unique()[0]
    df = pd.concat([df, na_df])
    return df


def plot_bars(
    plot_df,
    x="percentage",
    y="question",
    color="outcome",
    title="opinions",
    round_values=True,
    sort_order="descending",
    facet_row=None,
    palette=cool_warm_default,
    annot_col="outcome",
    fig_kw=None,
):
    """Make a stacked bar plot of the opinions of the whole sample, split by state and party."""

    if round_values:
        plot_df[x] = plot_df[x].round(3) * 100

    # sort by subquestion
    if facet_row is not None:
        plot_df[facet_row] = plot_df[facet_row].astype(int)
        plot_df = plot_df.sort_values(by=facet_row, ascending=True)

        # resize fig height to accommodate more facels
        n_facets = len(plot_df[facet_row].unique())
        fig_kw["height"] = fig_kw["height"] * n_facets * 0.5

    # sort by outcome
    print(f"sorting in {sort_order} order")
    if sort_order == "descending":
        plot_df = plot_df.sort_values(by="outcome", ascending=False)
    elif sort_order == "ascending":
        plot_df = plot_df.sort_values(by="outcome", ascending=True)
    else:
        pass

    # ----------------------------------------------------------------------
    # TODO: replace the placeholder with the actual annotation text column
    # ----------------------------------------------------------------------
    if annot_col is not None:
        plot_df["annote_text"] = (
            "placeholder: "
            + plot_df[annot_col].astype(str)
            + "<br>"
            + plot_df[x].round(3).astype(str)
            + "%"
        )

    # ----------------------------------------------------------------------

    else:
        plot_df["annote_text"] = plot_df[x].astype(str) + "%"

    # plot

    # set facet order
    facet_order = sorted(plot_df[facet_row].unique())
    category_orders = {facet_row: facet_order}

    # set stratify order
    if y == "party":
        category_orders[y] = ["Democrat", "Independent/Other", "Republican"]

    if facet_row is not None:
        fig = px.bar(
            plot_df,
            x=x,
            y=y,
            color=color,
            title=title,
            facet_row=facet_row,
            text="annote_text",
            category_orders=category_orders,
            color_discrete_sequence=palette,
            width=fig_kw["width"],
            height=fig_kw["height"],
        )
        fig.for_each_annotation(
            lambda a: a.update(text=a.text.replace(facet_row, "sub_q"))
        )

    else:
        fig = px.bar(
            plot_df,
            x=x,
            y=y,
            color=color,
            title=title,
            text="annote_text",
            category_orders=category_orders,
            color_discrete_sequence=palette,
            width=fig_kw["width"],
            height=fig_kw["height"],
        )

    fig.update_traces(texttemplate="%{text}", textposition="inside")
    fig.update_traces(
        marker_line_width=fig_kw["marker_line_width"],
        marker_line_color=fig_kw["marker_line_color"],
    )

    # remove y-axis labels if only one y value (i.e. question)
    if plot_df[y].nunique() == 1:
        fig.update_yaxes(
            tickmode="array",
            tickvals=plot_df[y],
            ticktext=[""] * len(plot_df[y]),
        )
    fig.update_layout(
        uniformtext_minsize=fig_kw["fontsize"], uniformtext_mode="hide"
    )
    fig.update_layout(showlegend=False)

    fig.show()


def run(
    question,
    subquestion,
    state=None,
    stratify=False,
    threshold=False,
    binarize_threshold=False,
    fig_kw=None,
):
    """Make plots for a given question, subquestion, and state.
    Optionally stratify by party and/or categorize by a threshold.
    """

    df = load_df(state, stratify)

    # check question
    assert (
        question in df["question"].unique()
    ), f"Question {question} not found in data."
    q_df = df[(df["question"] == question)].copy()

    # check subquestion
    if subquestion == "all":
        print("Plotting all subquestions as facets.")

    else:
        print(f"Plotting subquestion {subquestion}.")
        assert (
            subquestion
            in df[df["question"] == question]["sub_question"].unique()
        ), f"Subquestion {subquestion} not found in data."
        q_df = q_df[(q_df["sub_question"] == subquestion)].copy()

    print(f"n_subquestions: {len(q_df['sub_question'].unique())}")

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
            threshold in available_threshold_dict.keys()
        ), f"Threshold {threshold} not found in available thresholds."

        print(f"Thresholding at {threshold}.")

        if binarize_threshold:
            print(f"Binarizing threshold at {threshold}.")

            include_outcomes = [threshold]

            # set binary palette
            palette = binary_palette

        else:
            include_outcomes = [threshold] + available_threshold_dict[
                threshold
            ]

            # set palette for binary + "NA" option
            palette = ternary_palette

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
                "outcome": [threshold, na_outcome_label, agg_outcome_label]
            }

        else:
            # fill in the missing percentage values as the NA outcome
            q_df = fill_na_percentage(q_df, strata)
            cat_order = {"outcome": [threshold, na_outcome_label]}

        q_df["outcome"] = pd.Categorical(q_df["outcome"], cat_order["outcome"])
        q_df = q_df.sort_values(by="outcome")

        sort_order = "predetermined"

    else:
        # exclude categorical thresholds
        print("Excluding categorical thresholds.")

        q_df = q_df[~q_df["outcome"].isin(available_threshold_dict.keys())]
        sort_order = "descending"

        n_outcomes = len(q_df["outcome"].unique())
        print(f"n_outcomes: {n_outcomes}")
        if n_outcomes == 5:
            palette = cool_warm_5
        elif n_outcomes == 7:
            palette = cool_warm_7
        else:
            print(f"unknown number of outcomes: {n_outcomes}")

    print(f"possible_outcomes: {q_df['outcome'].unique()}")

    plot_bars(
        q_df,
        x="percentage",
        y=y,
        round_values=True,
        facet_row="sub_question",
        sort_order=sort_order,
        palette=palette,
        fig_kw=fig_kw,
    )

    return q_df


if __name__ == "__main__":

    # Example run
    q_df = run(
        question="q5",
        subquestion="all",
        stratify=True,
        threshold=False,
        binarize_threshold=True,
        fig_kw=fig_kw,
    )
