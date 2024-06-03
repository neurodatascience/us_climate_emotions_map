#!/usr/bin/env python
from functools import partial
from textwrap import wrap

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import sample_colorscale
from plotly.subplots import make_subplots

from .data_loader import DATA_DICTIONARIES, SURVEY_DATA

DEMOGRAPHICS_DICTIONARY = DATA_DICTIONARIES["demographics_dictionary.tsv"]
SAMPLEDESC_WHOLESAMPLE: pd.DataFrame = SURVEY_DATA[
    "sampledesc_wholesample.tsv"
]
SAMPLEDESC_STATE: pd.DataFrame = SURVEY_DATA["sampledesc_state.tsv"]

COL_DEMOGRAPHIC_VARIABLE = "demographic_variable"
COL_CATEGORY = "category"
COL_N = "n"
COL_PERCENTAGE = "percentage"

# these need a note explaining the percentage weighting
DEMOGRAPHIC_VARIABLES_WITH_ASTERISK = ["age", "sex", "race", "ethnicity"]

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
    "sex": (2, 1),
    "race": (3, 1),
    "ethnicity": (4, 1),
    "party": (5, 1),
    "student": (6, 1),
    "employed": (7, 1),
    "location": (8, 1),
    "hh_origin": (9, 1),
    IMPACTS_LABEL: (10, 1),
    Q2_LABEL: (11, 1),
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
    demographic_variable_to_display = (
        DEMOGRAPHICS_DICTIONARY.set_index(COL_DEMOGRAPHIC_VARIABLE)
        .loc[demographic_variable]
        .item()
    )
    if demographic_variable in DEMOGRAPHIC_VARIABLES_WITH_ASTERISK:
        demographic_variable_to_display = f"{demographic_variable_to_display}*"
    # if demographic_variable == Q2_LABEL:
    #     demographic_variable_to_display = wrap_text_label(
    #         demographic_variable_to_display, width=38
    #     )
    return demographic_variable_to_display


def get_category_to_display(category: str, demographic_variable: str):
    if demographic_variable == "student":
        category = {"yes": "student", "no": "non-student"}[category.lower()]
    return category.capitalize()


def make_descriptive_plot_traces(
    df: pd.DataFrame,
    demographic_variable: str,
    marker_color=None,
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
        y=df[COL_CATEGORY].apply(
            lambda x: get_category_to_display(x, demographic_variable)
        ),
        customdata=list(
            zip(
                df[COL_N],
                df[COL_CATEGORY].apply(
                    lambda x: get_category_to_display(x, demographic_variable)
                ),
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
            # text=[
            #     f"{percentage*100:.1f}% ({n})"
            #     for n, percentage in zip(df[COL_N], df[COL_PERCENTAGE])
            # ],
            hovertemplate=(
                "<b>%{customdata[1]}</b>: %{x:.2f}% (%{customdata[0]})"
                "<extra></extra>"
            ),
            marker_color=marker_color,
        ),
    )

    traces.append(
        bar_plot_trace_without_text(
            textposition="outside",
            text=df[COL_CATEGORY].apply(
                lambda x: get_category_to_display(x, demographic_variable)
            ),
            marker_color="rgba(0,0,0,0)",
            hoverinfo="skip",
        )
    )
    return traces


def wrap_text_label(text: str, width: int) -> pd.DataFrame:
    """Wraps string values of a column which are longer than the specified character length."""
    return "<br>".join(wrap(text=text, width=width, break_long_words=False))


def make_impact_plot_traces(
    df: pd.DataFrame, marker_color=None, text_wrap_width=10
):
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
        x = data_category[COL_DEMOGRAPHIC_VARIABLE].apply(
            get_demographic_variable_to_display
        )
        traces.append(
            go.Bar(
                x=x.apply(lambda x: wrap_text_label(x, width=text_wrap_width)),
                y=data_category[COL_PERCENTAGE] * 100,
                # text=[
                #     f"{percentage*100:.1f}% ({n})"
                #     for percentage, n in zip(
                #         data_category[COL_PERCENTAGE], data_category[COL_N]
                #     )
                # ],
                text=x.apply(
                    lambda x: wrap_text_label(x, width=text_wrap_width)
                ),
                customdata=list(zip(x, data_category[COL_N])),
                hovertemplate=(
                    "<b>%{customdata[0]}</b>"
                    ": %{y:.2f}% (%{customdata[1]})"
                    "<extra></extra>"
                ),
                marker_color=marker_color,
                hoverinfo="none",
                name=category,
            )
        )
    return traces


def make_descriptive_plots(
    state: str | None = None, margins=None, text_wrap_width=14
) -> go.Figure:

    if margins is None:
        margins = {"l": 0, "r": 0, "t": 20, "b": 0}

    # get data to plot
    if state is None:
        data = SAMPLEDESC_WHOLESAMPLE
    else:
        data = SAMPLEDESC_STATE.loc[SAMPLEDESC_STATE["state"] == state]

    row_heights = [
        n_categories + 0.5
        for n_categories in [2, 2, 3, 2, 3, 2, 3, 3, 5, 5, 8]
    ]

    # initialize figure
    fig = make_subplots(
        rows=len(row_heights),
        cols=1,
        row_heights=row_heights,
        subplot_titles=[
            get_demographic_variable_to_display(demographic_variable)
            for demographic_variable in SUBPLOT_POSITIONS
        ],
        vertical_spacing=0.04,
    )

    colorscale_step = 1 / (len(row_heights) - 1)
    colors = sample_colorscale(
        "turbo", np.arange(0, 1 + colorscale_step, colorscale_step)
    )

    # add plots
    demographic_variable_labels = []
    for demographic_variable in SUBPLOT_POSITIONS.keys():

        row, col = SUBPLOT_POSITIONS[demographic_variable]
        color = colors[row - 1]

        if demographic_variable == IMPACTS_LABEL:
            traces = make_impact_plot_traces(
                data, text_wrap_width=text_wrap_width, marker_color=color
            )
        else:
            traces = make_descriptive_plot_traces(
                data, demographic_variable, reverse=True, marker_color=color
            )
            if demographic_variable != Q2_LABEL:
                demographic_variable_labels.extend(
                    [demographic_variable] * len(traces[0].y)
                )

        for trace in traces:
            fig.add_trace(trace, row=row, col=col)

        if not demographic_variable == IMPACTS_LABEL:
            tickvals = ["" for _ in CATEGORY_ORDERS[demographic_variable]]
            ticktext = tickvals

            fig.update_yaxes(
                tickvals=tickvals,
                ticktext=ticktext,
                row=row,
                col=col,
            )
            fig.update_xaxes(
                range=[0, 105],
                tickvals=[0, 20, 40, 60, 80, 100],
                ticktext=["0", "20", "40", "60", "80", "100 (%)"],
                row=row,
                col=col,
            )
            fig.update_layout(bargap=0)

        else:
            fig.update_yaxes(
                range=[0, 100],
                tickvals=[0, 20, 40, 60, 80, 100],
                ticktext=["0", "20", "40", "60", "80", "(%)"],
                row=row,
                col=col,
            )
            fig.update_xaxes(
                tickvals=[],
                ticktext=[],
                row=row,
                col=col,
            )

        fig.update_yaxes(
            tickfont=dict(size=10),
            row=row,
            col=col,
        )
        fig.update_xaxes(
            tickfont=dict(size=10),
            row=row,
            col=col,
        )

    fig.update_layout(
        showlegend=False,
        margin=margins,
        template="plotly_white",
        font=dict(size=10),
    )
    fig.update_annotations(font_size=12)

    return fig


# if __name__ == "__main__":

#     # whole sample
#     fig = make_descriptive_plots()

#     # # specific state
#     # import numpy as np

#     # states: list = SAMPLEDESC_STATE["state"].unique().tolist()
#     # states.append(None)
#     # state = np.random.choice(states)
#     # print(f"state: {state}")
#     # fig = make_descriptive_plots(state=state)

#     fig.show()
