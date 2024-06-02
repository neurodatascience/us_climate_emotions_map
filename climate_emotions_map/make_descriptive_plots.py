#!/usr/bin/env python
from functools import partial
from textwrap import wrap

import pandas as pd
import plotly.graph_objects as go
from data_loader import DATA_DICTIONARIES, SURVEY_DATA
from plotly.subplots import make_subplots

DEMOGRAPHICS_DICTIONARY = DATA_DICTIONARIES["demographics_dictionary.tsv"]
SAMPLEDESC_WHOLESAMPLE: pd.DataFrame = SURVEY_DATA[
    "sampledesc_wholesample.tsv"
]
SAMPLEDESC_STATE: pd.DataFrame = SURVEY_DATA["sampledesc_state.tsv"]

COL_DEMOGRAPHIC_VARIABLE = "demographic_variable"
COL_CATEGORY = "category"
COL_N = "n"
COL_PERCENTAGE = "percentage"

# special handling of 7 weather impacts
IMPACTS_LABEL = "impact"
IMPACT_VARIABLES = sorted(
    ["drought", "flood", "heat", "hurricane", "smoke", "tornado", "wildfire"]
)

# special handling of q2
Q2_LABEL = "q2"

# order in the lists determines order in the plots
CATEGORY_ORDERS = {
    "age": [
        "under 18",
        "18+",
    ],
    "sex": [
        "Female",
        "Male",
    ],
    "party": [
        "Democrat",
        "Independent/Other",
        "Republican",
    ],
    "race": [
        "Black",
        "White",
        "Other",
    ],
    "ethnicity": [
        "Not Hispanic",
        "Hispanic",
    ],
    "student": [
        "No",
        "Yes",
    ],
    "employed": [
        "Not employed",
        "Employed - part time",
        "Employed - full time",
    ],
    "location": [
        "Rural",
        "Suburban",
        "Urban",
    ],
    "hh_origin": [
        "Working class",
        "Lower class",
        "Middle class",
        "Upper middle class",
        "Upper class",
    ],
    "drought": [
        "No",
        "Yes",
    ],
    "flood": [
        "No",
        "Yes",
    ],
    "heat": [
        "No",
        "Yes",
    ],
    "hurricane": [
        "No",
        "Yes",
    ],
    "smoke": [
        "No",
        "Yes",
    ],
    "tornado": [
        "No",
        "Yes",
    ],
    "wildfire": [
        "No",
        "Yes",
    ],
    Q2_LABEL: [
        "Very sure it is not happening",
        "Moderately sure it is not happening",
        "Slightly sure it is not happening",
        "Slightly sure it is happening",
        "Moderately sure it is happening",
        "Very sure it is happening",
        "Don't know",
    ],
}
CATEGORY_ORDERS.update(
    {
        "No": IMPACT_VARIABLES,
        "Yes": IMPACT_VARIABLES,
    }
)

SUBPLOT_POSITIONS = {
    "age": (1, 1),
    "sex": (1, 1),
    "race": (1, 1),
    "ethnicity": (1, 1),
    "party": (1, 1),
    "student": (1, 1),
    "employed": (1, 1),
    "location": (1, 1),
    "hh_origin": (1, 1),
    IMPACTS_LABEL: (4, 1),
    Q2_LABEL: (5, 1),
}


def get_categories_dict(df: pd.DataFrame) -> dict:
    """
    Get a dictionary of categories for each demographic variable.

    Starting point for manually making CATEGORY_ORDER.
    """
    df = df.copy(deep=True)
    df = df.drop_duplicates(subset=[COL_DEMOGRAPHIC_VARIABLE, COL_CATEGORY])
    df = df.loc[:, [COL_DEMOGRAPHIC_VARIABLE, COL_CATEGORY]]
    df[COL_CATEGORY] = df[COL_CATEGORY].apply(lambda x: [x])
    df = df.groupby(COL_DEMOGRAPHIC_VARIABLE).agg({COL_CATEGORY: "sum"})
    return df.to_dict()


def get_demographic_variable_to_display(demographic_variable: str):
    return (
        DEMOGRAPHICS_DICTIONARY.set_index(COL_DEMOGRAPHIC_VARIABLE)
        .loc[demographic_variable]
        .item()
    )


def get_category_to_display(category: str):
    return category.capitalize()


def make_descriptive_plot_traces(
    df: pd.DataFrame,
    demographic_variable: str,
    reverse=True,
) -> go.Bar:
    """
    Make a single plot for a descriptive demographic variable.

    Parameters
    ----------
    df : pd.DataFrame
        Data to plot. Expect columns: "demographic_variable" "category", "n",
        and "percentage".
    demographic_variable : str
        Demographic variable to plot.
    """
    # subset the data
    df: pd.DataFrame = df.loc[
        df[COL_DEMOGRAPHIC_VARIABLE] == demographic_variable
    ].copy()

    # use custom category order
    df[COL_CATEGORY] = pd.Categorical(
        df[COL_CATEGORY], categories=CATEGORY_ORDERS[demographic_variable]
    )
    df = df.sort_values(COL_CATEGORY, ascending=not reverse)

    bar_plot_trace_without_text = partial(
        go.Bar,
        x=df[COL_PERCENTAGE] * 100,
        # y=(
        #     [get_demographic_variable_to_display(demographic_variable)]
        #     * len(df[COL_CATEGORY].apply(get_category_to_display))
        # ),
        y=df[COL_CATEGORY].apply(get_category_to_display),
        hoverinfo="none",
        customdata=list(
            zip(
                df[COL_N],
                df[COL_CATEGORY].apply(get_category_to_display),
            )
        ),
        orientation="h",
        name=demographic_variable,
        offsetgroup=0,
    )

    traces = []
    # make the bar plot
    traces.append(
        bar_plot_trace_without_text(
            textposition="inside",
            text=[
                f"{percentage*100:.1f}% ({n})"
                for n, percentage in zip(df[COL_N], df[COL_PERCENTAGE])
            ],
            # hovertemplate=(
            #     # f"<b>{get_demographic_variable_to_display(demographic_variable)}</b>"
            #     "<b>%{customdata[1]}</b>: %{x:.2f}% (%{customdata[0]})"
            #     "<extra></extra>"
            # ),
        ),
    )

    traces.append(
        bar_plot_trace_without_text(
            textposition="outside",
            text=df[COL_CATEGORY].apply(get_category_to_display),
            marker_color="rgba(0,0,0,0)",
        )
    )
    return traces


def wrap_df_column_values(series: pd.Series, width: int) -> pd.DataFrame:
    """Wraps string values of a column which are longer than the specified character length."""
    series = series.map(
        lambda value: "<br>".join(
            wrap(text=value, width=width, break_long_words=False)
        ),
        na_action="ignore",
    )
    return series


def make_impact_plot_traces(df: pd.DataFrame):
    data_impact = df.loc[
        df[COL_DEMOGRAPHIC_VARIABLE].isin(IMPACT_VARIABLES)
    ].copy()
    data_impact[COL_DEMOGRAPHIC_VARIABLE] = pd.Categorical(
        data_impact[COL_DEMOGRAPHIC_VARIABLE], categories=IMPACT_VARIABLES
    )
    data_impact = data_impact.sort_values(COL_DEMOGRAPHIC_VARIABLE)
    traces = []
    for category in ["Yes"]:
        data_category = data_impact.loc[data_impact[COL_CATEGORY] == category]
        traces.append(
            go.Bar(
                x=wrap_df_column_values(
                    data_category[COL_DEMOGRAPHIC_VARIABLE].apply(
                        get_demographic_variable_to_display
                    ),
                    width=15,
                ),
                y=data_category[COL_PERCENTAGE] * 100,
                text=[
                    f"{percentage*100:.1f}% ({n})"
                    for percentage, n in zip(
                        data_category[COL_PERCENTAGE], data_category[COL_N]
                    )
                ],
                # customdata=data_category[COL_PERCENTAGE] * 100,
                # hovertemplate=(
                #     "<b>%{x}</b>"
                #     f"<br>{category}: %{{y}} (%{{customdata:.1f}}%)"
                #     "<extra></extra>"
                # ),
                hoverinfo="none",
                name=category,
            )
        )
    return traces


def make_descriptive_plots(state: str | None = None) -> go.Figure:

    # get data to plot
    if state is None:
        data = SAMPLEDESC_WHOLESAMPLE
    else:
        data = SAMPLEDESC_STATE.loc[SAMPLEDESC_STATE["state"] == state]

    # initialize figure
    fig = make_subplots(
        rows=5,
        cols=1,
        specs=[
            [{"rowspan": 3}],
            [None],
            [None],
            [{"rowspan": 1}],
            [{"rowspan": 1}],
        ],
        subplot_titles=[
            "Demographic information",
            get_demographic_variable_to_display(IMPACTS_LABEL),
            get_demographic_variable_to_display(Q2_LABEL),
        ],
    )

    # add plots
    demographic_variable_labels = []
    for demographic_variable in reversed(SUBPLOT_POSITIONS.keys()):

        row, col = SUBPLOT_POSITIONS[demographic_variable]

        if demographic_variable == IMPACTS_LABEL:
            traces = make_impact_plot_traces(data)
        else:
            traces = make_descriptive_plot_traces(data, demographic_variable)
            if demographic_variable != Q2_LABEL:
                demographic_variable_labels.extend(
                    [demographic_variable] * len(traces[0].y)
                )

        for trace in traces:
            fig.add_trace(trace, row=row, col=col)

        if not demographic_variable == IMPACTS_LABEL:
            if demographic_variable == Q2_LABEL:
                tickvals = ["" for _ in CATEGORY_ORDERS[demographic_variable]]
                ticktext = tickvals
            else:
                df_y_ticks = pd.DataFrame(demographic_variable_labels)
                df_y_ticks = (
                    df_y_ticks.reset_index().groupby(0).mean().reset_index()
                )
                # print(df_y_ticks)
                tickvals = df_y_ticks["index"]
                ticktext = df_y_ticks[0].apply(
                    get_demographic_variable_to_display
                )
            fig.update_yaxes(
                tickvals=tickvals,
                ticktext=ticktext,
                row=row,
                col=col,
            )
            fig.update_xaxes(range=[0, 100], row=row, col=col)

    fig.update_layout(
        showlegend=False,
        margin={"l": 0, "r": 0, "t": 20, "b": 0},
    )

    return fig


if __name__ == "__main__":

    # whole sample
    fig = make_descriptive_plots()

    # # specific state
    # import numpy as np

    # states: list = SAMPLEDESC_STATE["state"].unique().tolist()
    # states.append(None)
    # state = np.random.choice(states)
    # print(f"state: {state}")
    # fig = make_descriptive_plots(state=state)

    fig.show()
