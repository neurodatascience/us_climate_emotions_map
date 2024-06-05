import copy
from textwrap import wrap

import pandas as pd
import plotly.express as px

from .data_loader import DATA_DICTIONARIES, SUBQUESTION_ORDER, SURVEY_DATA

THEME = "plotly_white"
LAYOUTS = {
    "margin": {"l": 30, "r": 30, "t": 30, "b": 20},
    # TODO: Remove
    "title": {  # figure title position properties, see https://plotly.com/python/reference/layout/#layout-title
        "yanchor": "bottom",
        "yref": "paper",
        # "pad": {"t": 10},
        "y": 1,
    },
    # NOTE: to debug the title layout, use the "plotly" theme to make the plot area visible
}
FACET_LAYOUTS = {
    "title_fsize": 14,
    "facet_row_spacing": 40,
    "wrap_width": 25,
}

# TODO: Revisit
# Default figure parameters
DEFAULT_FIG_KW = {
    "fontsize": 10,
    # width not used, controlled instead by the app layout
    "width": 800,
    "height": 130,
    "marker_line_width": 1,
    "marker_line_color": "black",
}

# Custom palettes
PALETTES_BY_LENGTH = {
    # cool_warm_5
    5: ["#f94144", "#f3722c", "#f8961e", "#43aa8b", "#577590"],
    # cool_warm_7
    7: [
        "#f94144",
        "#f3722c",
        "#f8961e",
        "#90be6d",
        "#43aa8b",
        "#4d908e",
        "#577590",
    ],
    # binary_palette
    2: ["#f8961e", "#43aa8b"],
    # ternary_palette
    3: ["#f8961e", "#d5bdaf", "#43aa8b"],
}

# cool_warm_default = [
#     "#f94144",
#     "#f3722c",
#     "#f8961e",
#     "#f9844a",
#     "#f9c74f",
#     "#90be6d",
#     "#43aa8b",
#     "#4d908e",
#     "#577590",
#     "#277da1",
# ]

# Global labels
# Label used for custom outcome created to aggregate over unaccounted for outcome proportions for 3+ and 4+ thresholds
# (i.e., for subquestions that have >5 response options)
AGG_OUTCOME_LABEL = "other"
# Label used for custom outcome created to fill in the missing proportion when binarizing data based on a threshold
NA_OUTCOME_LABEL = "not3+"

# Pre-defined thresholds
available_threshold_dict = {"3+": ["1", "2"], "4+": ["1", "2", "3"]}

PARTY_ORDER = ["Democrat", "Independent/Other", "Republican"]


def load_df(state: str | None, stratify: bool) -> pd.DataFrame | None:
    """Return the opinions data for the whole sample, stratified by state, or stratified by party."""
    if state is None and not stratify:
        return SURVEY_DATA["opinions_wholesample.tsv"]
    if state is not None:
        return SURVEY_DATA["opinions_state.tsv"]
    if stratify:
        return SURVEY_DATA["opinions_party.tsv"]
    return None


def wrap_column_text(df: pd.DataFrame, column: str, width: int) -> pd.Series:
    """Wrap string values of a column which are longer than the specified character length."""
    df = df.copy()

    # Create a mask for rows where the percentage < 50
    mask = df["percentage"] < 50

    # Apply wrapping to only rows where the mask is True
    # Need to worry about NaNs?
    df.loc[mask, column] = df.loc[mask, column].apply(
        lambda value: "<br>".join(
            wrap(text=str(value), width=width, break_long_words=False)
        )
    )
    return df[column]


# TODO: Remove all logic related to aggregating - not needed for the current data
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


def fill_na_percentage(df: pd.DataFrame):
    """
    Fill in the missing percentage values for the NA outcome.
    This is used only when the response data is thresholded at a specific endorsement level.
    """
    df_inverted = df.copy()
    df_inverted["percentage"] = 1 - df_inverted["percentage"]
    df_inverted["outcome"] = NA_OUTCOME_LABEL

    # Combine the original and the percentage-inverted DataFrames
    return pd.concat([df, df_inverted]).sort_index().reset_index(drop=True)


def get_subquestion_text(question: str, subquestion: str):
    """Get the full text for a subquestion."""
    dict_df = DATA_DICTIONARIES["subquestion_dictionary.tsv"]
    question_text = dict_df.loc[
        (dict_df["question"] == question)
        & (dict_df["sub_question"] == subquestion),
        "full_text",
    ]

    return question_text.values[0]


def plot_bars(
    plot_df,
    x="percentage",
    y="question",
    color="outcome",
    title=None,  # "opinions" - TODO: remove this argument?
    round_values=True,
    sort_order="descending",
    facet_row=None,
    facet_order=None,
    palette=None,
    annot_col="outcome",
    fig_kw=None,
) -> px.bar:
    """Make a stacked bar plot of the opinions of the whole sample, split by state and party."""
    if round_values:
        plot_df[x] = plot_df[x].round(3) * 100

    # sort by subquestion

    if facet_row is not None:
        # TODO: Check if this part is necessary - seems to mess things up
        # order = SUBQUESTION_ORDER[question]  # plot_df["question"].unique()[0]
        # plot_df[facet_row] = pd.Categorical(plot_df[facet_row], order)
        # plot_df = plot_df.sort_values(by=facet_row)

        # plot_df[facet_row] = plot_df[facet_row].astype(int)
        # plot_df = plot_df.sort_values(by=facet_row, ascending=True)

        # resize fig height to accommodate more facets
        n_facets = len(plot_df[facet_row].unique())
        fig_kw["height"] = fig_kw["height"] * n_facets  # * 0.5

    # sort by outcome
    print(f"sorting in {sort_order} order")
    if sort_order == "descending":
        plot_df = plot_df.sort_values(by="outcome", ascending=False)
    elif sort_order == "ascending":
        plot_df = plot_df.sort_values(by="outcome", ascending=True)
    else:
        pass

    # ----------------------------------------------------------------------
    # TODO: Maybe refactor to avoid creating new columns every time
    # Get full text labels for each outcome
    # ----------------------------------------------------------------------
    outcome_dict_df = DATA_DICTIONARIES["outcome_dictionary.tsv"].copy()
    plot_df["key"] = (
        plot_df["question"].astype(str) + "_" + plot_df[annot_col].astype(str)
    )
    outcome_dict_df["key"] = (
        outcome_dict_df["question"] + "_" + outcome_dict_df[annot_col]
    )

    full_text_series = outcome_dict_df.set_index("key")["full_text"]
    plot_df["full_text"] = plot_df["key"].map(full_text_series)
    plot_df["annotate_text"] = (
        wrap_column_text(
            df=plot_df, column="full_text", width=FACET_LAYOUTS["wrap_width"]
        )
        + "<br>"
        + plot_df[x].round(3).astype(str)
        + "%"
    )

    # Clean up temporary keys
    plot_df.drop(columns=["key"], inplace=True)
    # ----------------------------------------------------------------------
    # NOTE: If human-readable labels not wanted, can use the outcomes directly:
    # plot_df["annotate_text"] = plot_df[annot_col] + "<br>" + plot_df[x].astype(str) + "%"

    # plot

    # set facet order
    category_orders = {facet_row: facet_order}

    # Define custom hover data
    # TODO: Do we need the raw outcomes in the hover data? "outcome" / color column
    custom_data = ["full_text"]
    # <extra></extra> hides the secondary box that appears when hovering over the bars
    hovertemplate = "<br>".join(
        [
            "Outcome: %{customdata[0]}",
            "Percentage: %{x:.1f}%",
            "<extra></extra>",
        ]
    )

    # set stratify order
    if y == "party":
        category_orders[y] = PARTY_ORDER

        # Define custom hover data
        custom_data.append("party")
        hovertemplate = "<br>".join(
            [
                "<b>%{customdata[1]}</b>",
                hovertemplate,
            ]
        )

    # if plot_df[facet_row].nunique() > 1:
    if facet_row is not None:
        fig = px.bar(
            plot_df,
            x=x,
            y=y,
            color=color,
            title=title,
            facet_col=facet_row,
            facet_col_wrap=1,
            facet_row_spacing=(
                FACET_LAYOUTS["facet_row_spacing"] / fig_kw["height"]
            ),
            text="annotate_text",
            category_orders=category_orders,
            custom_data=custom_data,
            color_discrete_sequence=palette,
            # width=fig_kw["width"],
            height=fig_kw["height"],
            template=THEME,
        )

        # TODO: Add state/"National" as well?
        # Update hover data
        fig.update_traces(hovertemplate=hovertemplate)

        # # Update facet titles with subquestion text
        # fig.for_each_annotation(
        #     lambda a: a.update(
        #         text=get_subquestion_text(
        #             question, subquestion=a.text.split("=")[-1]
        #         ),
        #         # Ensure that facet title is left-aligned
        #         xanchor="left",
        #         x=0,
        #         xref="paper",
        #     )
        # )

    # TODO: See if we can remove the else block
    else:
        fig = px.bar(
            plot_df,
            x=x,
            y=y,
            color=color,
            title=title,
            text="annotate_text",
            category_orders=category_orders,
            color_discrete_sequence=palette,
            # width=fig_kw["width"],
            height=fig_kw["height"],
            template=THEME,
        )

    # TODO: Revisit to add thicker lines between bars
    # fig.add_vline(x=0.5, line_color="black")
    # fig.add_shape(go.layout.Shape(type="line",
    #     yref="paper",
    #     xref="x",
    #     x0=1,
    #     y0=-2,
    #     x1=1,
    #     y1=2,
    #     line=dict(color="black", width=3),),
    #     row=i,
    #     col=j)

    fig.update_xaxes(
        showgrid=False,
        # showline=False,
        zeroline=False,
        title=None,
        # TODO: See if we want to remove the x tick labels
        showticklabels=False,
    )
    fig.update_yaxes(showgrid=False, title=None)
    fig.update_layout(margin=LAYOUTS["margin"])

    fig.update_traces(
        texttemplate="%{text}",
        textposition="inside",
        insidetextanchor="middle",
    )
    # fig.update_traces(
    #     marker_line_width=fig_kw["marker_line_width"],
    #     marker_line_color=fig_kw["marker_line_color"],
    # )

    # remove y-axis labels if only one y value (i.e. question)
    if plot_df[y].nunique() == 1:
        fig.update_yaxes(showticklabels=False)

    fig.update_layout(
        uniformtext_minsize=fig_kw["fontsize"], uniformtext_mode="hide"
    )
    fig.update_layout(showlegend=False)

    return fig


def make_stacked_bar(
    question: str,
    subquestion: str,
    state: str | None = None,
    stratify: bool = False,
    threshold: str | None = None,
    binarize_threshold: bool = False,
    palettes: dict = None,
    fig_kw: dict = None,
) -> px.bar:
    """
    Make plots for a given question, subquestion, and state.
    Optionally stratify by party and/or categorize by a threshold.

    Parameters
    ----------
    question : str
        The question ID (e.g. "q1").
    subquestion : str
        The subquestion ID (e.g. "1"), or "all" to plot all subquestions as facets.
    state : str, optional
        The state to filter the data by. The default is None. NOTE: This is expected to be None if stratify is True.
    stratify : bool, optional
        Whether to stratify the data by party. The default is False.
    threshold : str, optional
        The outcome ID for the Likert endorsement level to threshold at (e.g. "3+"). The default is None.
    binarize_threshold : bool, optional
        Whether to binarize the data based on the threshold, meaning that the stacked bar will include two segments, one
        representing the threshold and another segment representing 100% - the proportion for the threshold. The default is False.
    palettes : dict, optional
        A dictionary of color palettes for different numbers of outcomes. The default is None.
    fig_kw : dict, optional
        A dictionary of figure parameters. The default is None.
    """
    if fig_kw is None:
        # We need to make a deep copy to avoid modifying the default values!
        fig_kw = copy.deepcopy(DEFAULT_FIG_KW)

    if palettes is None:
        palettes = PALETTES_BY_LENGTH

    df = load_df(state, stratify)

    # check question
    # assert (
    #     question in df["question"].unique()
    # ), f"Question {question} not found in data."
    # TODO: Remove temporary workaround for "noanswer" subquestion
    q_df = df.loc[
        (df["question"] == question) & (df["sub_question"] != "noanswer")
    ].copy()

    # check subquestion
    if subquestion == "all":
        print("Plotting all subquestions as facets.")

    else:
        print(f"Plotting subquestion {subquestion}.")
        # assert (
        #     subquestion
        #     in df[df["question"] == question]["sub_question"].unique()
        # ), f"Subquestion {subquestion} not found in data."
        q_df = q_df.loc[(q_df["sub_question"] == subquestion)].copy()

    print(f"n_subquestions: {len(q_df['sub_question'].unique())}")

    y = "question"

    # Check if looking for particular state
    if state:
        # assert (
        #     state in q_df["state"].unique()
        # ), f"State {state} not found in data."

        print(f"Filtering for state {state}.")
        q_df = q_df[q_df["state"] == state]

    if stratify:
        strata = "party"
        y = strata
        # assert strata in q_df.columns, f"{strata} column not found in data."

        # Resize fig height to accommodate bars for different parties
        fig_kw["height"] = fig_kw["height"] * 1.75

        print("Stratifying by {strata}.")

    else:
        strata = None

    if threshold:
        # assert (
        #     threshold in available_threshold_dict
        # ), f"Threshold {threshold} not found in available thresholds."

        print(f"Thresholding at {threshold}.")

        if binarize_threshold:
            print(f"Binarizing threshold at {threshold}.")

            include_outcomes = [threshold]

            # set binary palette
            palette = palettes[2]

        else:
            include_outcomes = [threshold] + available_threshold_dict[
                threshold
            ]

            # set palette for binary + "NA" option
            palette = palettes[3]

        print(f"include_outcomes: {include_outcomes}")
        q_df = q_df[q_df["outcome"].isin(include_outcomes)]

        if not binarize_threshold:
            # aggregate outcomes less than the threshold
            q_df = aggregate_outcome_subset(
                q_df, available_threshold_dict[threshold], strata
            )

            # fill in the missing percentage values as the NA outcome
            q_df = fill_na_percentage(q_df)

            cat_order = {
                "outcome": [threshold, NA_OUTCOME_LABEL, AGG_OUTCOME_LABEL]
            }

        else:
            # fill in the missing percentage values as the NA outcome
            q_df = fill_na_percentage(q_df)
            cat_order = {"outcome": [threshold, NA_OUTCOME_LABEL]}

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

        try:
            palette = palettes[n_outcomes]
        except KeyError:
            print(f"unknown number of outcomes: {n_outcomes}")

    print(f"possible_outcomes: {q_df['outcome'].unique()}")

    fig = plot_bars(
        q_df,
        x="percentage",
        y=y,
        round_values=True,
        facet_row="sub_question",
        facet_order=SUBQUESTION_ORDER[question],
        sort_order=sort_order,
        palette=palette,
        fig_kw=fig_kw,
    )

    # TODO: See if this needs refactoring
    # Update facet titles with subquestion text
    if q_df["sub_question"].nunique() > 1:
        fig.for_each_annotation(
            lambda a: a.update(
                text=get_subquestion_text(
                    question, subquestion=a.text.split("=")[-1]
                ),
                font_size=FACET_LAYOUTS["title_fsize"],
                # Ensure that facet title is left-aligned
                xanchor="left",
                x=0,
                xref="paper",
            )
        )
    else:
        # Remove facet title
        fig.update_annotations(text="")

    return fig


# if __name__ == "__main__":

#     # Example run
#     fig = make_stacked_bar(
#         question="q5",
#         subquestion="all",
#         stratify=False,
#         threshold="3+",
#         binarize_threshold=True,
#         fig_kw=default_fig_kw,
#         # fig_kw={
#         #     "fontsize": 10,
#         #     "width": 800,
#         #     "height": 300,
#         #     "marker_line_width": 1,
#         #     "marker_line_color": "black",
#         # }
#     )
#     fig.show()
