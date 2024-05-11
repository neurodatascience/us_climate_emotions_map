#!/usr/bin/env python
import pandas as pd
import plotly.graph_objects as go
from data_loader import SURVEY_DATA
from plotly.subplots import make_subplots

SAMPLEDESC_WHOLESAMPLE: pd.DataFrame = SURVEY_DATA[
    "sampledesc_wholesample.tsv"
]
SAMPLEDESC_STATE: pd.DataFrame = SURVEY_DATA["sampledesc_state.tsv"]

COL_DEMOGRAPHIC_VARIABLE = "demographic_variable"
COL_CATEGORY = "category"
COL_N = "n"
COL_PERCENTAGE = "percentage"

# special handling of 7 weather impacts
IMPACTS_LABEL = "impacts"
IMPACT_VARIABLES = sorted(
    ["drought", "flood", "heat", "hurricane", "smoke", "tornado", "wildfire"]
)

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
    "q2": [
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
    "sex": (1, 3),
    "party": (1, 5),
    "race": (2, 1),
    "ethnicity": (2, 4),
    "student": (3, 1),
    "employed": (3, 4),
    "location": (4, 1),
    "hh_origin": (4, 4),
    IMPACTS_LABEL: (5, 1),
    "q2": (6, 1),
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
    if demographic_variable == "hh_origin":
        demographic_variable = "household origin"
    elif demographic_variable == "q2":
        demographic_variable = (
            "How sure are you that climate change is or is not happening?"
        )
    return demographic_variable.capitalize()


def get_category_to_display(category: str):
    return category.capitalize()


def make_descriptive_plot(
    df: pd.DataFrame, demographic_variable: str, **kwargs
) -> go.Bar:
    """
    Make a single plot for a descriptive demographic variable.

    Extra kwargs are passed to plotly.express.bar()

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
    df = df.sort_values(COL_CATEGORY)

    # make the bar plot
    bar_plot = go.Bar(
        x=df[COL_CATEGORY].apply(get_category_to_display),
        y=df[COL_N],
        customdata=df[COL_PERCENTAGE] * 100,
        # text=[
        #     f"{n} ({percentage*100:.1f}%)"
        #     for n, percentage in zip(df[COL_N], df[COL_PERCENTAGE])
        # ],
        hovertemplate=(
            f"<b>{get_demographic_variable_to_display(demographic_variable)}</b>"
            "<br>%{x}: %{y} (%{customdata:.1f}%)"
            "<extra></extra>"
        ),
        name=demographic_variable,
    )
    return bar_plot


def make_impact_plot_traces(data: pd.DataFrame):
    data_impact = data.loc[
        data[COL_DEMOGRAPHIC_VARIABLE].isin(IMPACT_VARIABLES)
    ].copy()
    data_impact[COL_DEMOGRAPHIC_VARIABLE] = pd.Categorical(
        data_impact[COL_DEMOGRAPHIC_VARIABLE], categories=IMPACT_VARIABLES
    )
    data_impact = data_impact.sort_values(COL_DEMOGRAPHIC_VARIABLE)
    traces = []
    for category in ["No", "Yes"]:
        data_category = data_impact.loc[data_impact[COL_CATEGORY] == category]
        traces.append(
            go.Bar(
                x=data_category[COL_DEMOGRAPHIC_VARIABLE].apply(
                    get_demographic_variable_to_display
                ),
                y=data_category[COL_N],
                customdata=data_category[COL_PERCENTAGE] * 100,
                hovertemplate=(
                    "<b>%{x}</b>"
                    f"<br>{category}: %{{y}} (%{{customdata:.1f}}%)"
                    "<extra></extra>"
                ),
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
        rows=6,
        cols=6,
        specs=[
            [{"colspan": 2}, None, {"colspan": 2}, None, {"colspan": 2}, None],
            [{"colspan": 3}, None, None, {"colspan": 3}, None, None],
            [{"colspan": 3}, None, None, {"colspan": 3}, None, None],
            [{"colspan": 3}, None, None, {"colspan": 3}, None, None],
            [{"colspan": 6}, None, None, None, None, None],
            [{"colspan": 6}, None, None, None, None, None],
        ],
        subplot_titles=[
            get_demographic_variable_to_display(demographic_variable)
            for demographic_variable in SUBPLOT_POSITIONS.keys()
        ],
    )

    # add plots
    for demographic_variable in SUBPLOT_POSITIONS.keys():

        row, col = SUBPLOT_POSITIONS[demographic_variable]

        if demographic_variable == IMPACTS_LABEL:
            for trace in make_impact_plot_traces(data):
                fig.add_trace(trace, row=row, col=col)
        else:
            fig.add_trace(
                make_descriptive_plot(data, demographic_variable),
                row=row,
                col=col,
            )

    # turn off legend
    fig.update_layout(showlegend=False)

    return fig


if __name__ == "__main__":

    # print(get_categories_dict(SAMPLEDESC_WHOLESAMPLE))

    # # whole sample
    # fig = make_descriptive_plots()

    # specific state
    import numpy as np

    states: list = SAMPLEDESC_STATE["state"].unique().tolist()
    states.append(None)
    state = np.random.choice(states)
    print(f"state: {state}")
    fig = make_descriptive_plots(state=state)

    fig.show()
