import pandas as pd
import plotly.graph_objects as go

from .data_loader import DATA_DICTIONARIES, GEOJSON_OBJECTS, SURVEY_DATA

survey_states = GEOJSON_OBJECTS["survey_states.json"]

opinions_state = SURVEY_DATA["opinions_state.tsv"]
samplesizes_state = SURVEY_DATA["samplesizes_state.tsv"]
sampledesc_state = SURVEY_DATA["sampledesc_state.tsv"]

state_abbreviations = DATA_DICTIONARIES["state_abbreviations.tsv"]

impact_emoji_map = {
    "drought": "🏜️",
    "flood": "💧",
    "heat": "🥵",
    "hurricane": "🌀",
    "smoke": "🏭",
    "tornado": "🌪️",
    "wildfire": "🔥",
}


def get_state_abbrevs_in_long_format(
    state_abbreviations: pd.DataFrame = state_abbreviations,
):
    # put the state abbreviations in a format where there's one row per state
    # i.e., flatten out the clusters
    # but still keep the "state" column as the original state/cluster name
    states = []
    single_states = []
    abbrevs = []
    for _, row in state_abbreviations.iterrows():
        # a row would look like this Alaska, Idaho, Montana, Wyoming (Cluster F) and we don't want the cluster name too
        state_list = row["state"].split(" (")[0].split(", ")
        single_states.extend(state_list)
        abbrev_list = row["state_abbreviated"].split(", ")
        abbrevs.extend(iter(abbrev_list))
        # values in the "states" column can either be single states or clusters of several states.
        # for clusters, we have to repeat the cluster name once for each state in the cluster
        # so we can have one row per state - whether the state is in a cluster or not
        states.extend([row["state"]] * len(state_list))
    state_abbrevs_long = pd.DataFrame(
        data={
            "state": states,
            "single_state": single_states,
            "state_abbreviated": abbrevs,
        }
    )
    return state_abbrevs_long


def make_map(
    question: str,
    sub_question: str,
    outcome: str,
    clicked_state: str | None = None,
    impact: str | None = None,
    show_impact_as_gradient=True,
    opinion_colormap: str | None = "Greens",
    impact_colormap: str | None = "OrRd",
    clicked_state_marker: dict | None = None,
    impact_marker_size_scale: float = 1.0,
    colormap_range_padding=10,
    margins=None,
) -> go.Figure:
    """Generate choropleth map showing opinion and/or impact data.

    Parameters
    ----------
    question : str
        The question to plot (for opinion data).
    sub_question : str
        The subquestion to plot (for opinion data).
    outcome : str
        The outcome to plot (for opinion data).
    clicked_state : str | None, optional
        Clicked state to highlight, by default None.
    impact : str | None, optional
        Name of impact to plot, by default None
    show_impact_as_gradient : bool, optional
        Whether to show impact information in the base map (replacing opinion
        data) instead of as an additional scatter plot, by default True
    opinion_colormap : str | None, optional
        Colormap for the opinion data, by default "Greens"
    impact_colormap : str | None, optional
        Colormap for the impact data, by default "Oranges"
    clicked_state_marker : dict | None, optional
        Configuration for the clicked state (e.g., highlighting color). By
        default it will make the outline thicker and yellow
    impact_marker_size_scale : float, optional
        Scale factor for the impact marker size, by default 1.0
    colormap_range_padding : int, optional
        Padding for the colormap vmin/vmax range, by default 10
    margins : dict | None, optional
        Margins for the Plotly figure, by default 30 everywhere

    Returns
    -------
    go.Figure

    Raises
    ------
    RuntimeError
        If the given question/subquestion/outcome or impact are invalid.
    """
    # constants
    col_location = "state"
    col_color = "percentage"
    col_color_opinion = f"{col_color} (opinion)"
    col_color_impact = f"{col_color} (impact)"

    # default values
    if clicked_state_marker is None:
        clicked_state_marker = dict(line=dict(width=4, color="#2a3f5f"))
    if margins is None:
        margins = {"l": 30, "r": 30, "t": 30, "b": 30}

    # get the state abbreviations in long format
    # "state" (i.e. state or cluster), "single_state", "state_abbreviated"
    state_abbrevs_long = get_state_abbrevs_in_long_format()

    # get the question data
    df_opinions = opinions_state.loc[
        (opinions_state["question"] == question)
        & (opinions_state["sub_question"] == sub_question)
        & (opinions_state["outcome"] == outcome)
    ]

    if len(df_opinions) == 0:
        raise RuntimeError(
            f"No data found for question {question} ({type(question)})"
            f", sub_question {sub_question} ({type(sub_question)})"
            f", outcome {outcome} ({type(outcome)})"
        )

    # We have to rename the column `col_color` (e.g. "percentage") with a suffix for `opinion`
    # because we later merge `opinion` and `impact` data on `col_color` in the same table
    # and we want to differentiate between the two
    df_to_plot = df_opinions.rename(columns={col_color: col_color_opinion})
    df_to_plot[col_color_opinion] *= 100

    # get impact data if requested
    if impact is not None:
        df_impacts = sampledesc_state.loc[
            (sampledesc_state["demographic_variable"] == impact)
            & (sampledesc_state["category"] == "Yes")
        ]
        if len(df_impacts) == 0:
            raise RuntimeError(
                f"No impact data found for {impact} ({type(impact)})"
            )

        df_to_plot = df_to_plot.merge(
            df_impacts[[col_location, col_color]].rename(
                columns={col_color: col_color_impact}
            ),
            on=col_location,
        )
        df_to_plot[col_color_impact] *= 100

    if impact is not None and show_impact_as_gradient:
        col_gradient = col_color_impact
        colormap = impact_colormap
    else:
        col_gradient = col_color_opinion
        colormap = opinion_colormap

    # get minimum/maximum values for scaling the colormap
    vmin = max(0, df_to_plot[col_gradient].min() - colormap_range_padding)
    vmax = min(100, df_to_plot[col_gradient].max() + colormap_range_padding)

    # initialize the figure
    fig = go.Figure()

    # plot the `col_gradient` data on a map
    # do not show the hoverboxes here because for some reason they are not centered properly
    fig.add_choropleth(
        locations=df_to_plot[col_location],
        geojson=survey_states,
        z=df_to_plot[col_gradient],
        zmin=vmin,
        zmax=vmax,
        colorscale=colormap,
        colorbar_title=col_gradient.capitalize(),
        name="main_map",
        hoverinfo="none",  # no hoverbox but click events are still emitted (?)
    )

    # add outline for clicked state
    if clicked_state is not None:
        df_to_plot_clicked = df_to_plot[
            df_to_plot[col_location] == clicked_state
        ]
        fig.add_choropleth(
            locations=df_to_plot_clicked[col_location],
            geojson=survey_states,
            z=df_to_plot_clicked[col_gradient],
            zmin=vmin,
            zmax=vmax,
            colorscale=colormap,
            hoverinfo="skip",
            name="clicked_state",
            marker=clicked_state_marker,
            showscale=False,
        )

    # add hover information
    df_hover_data = state_abbrevs_long.merge(
        df_to_plot,
        on=col_location,
    ).merge(
        samplesizes_state,
        on=col_location,
    )
    # if gradient only
    customdata_cols = [col_location, "n"]
    hovertemplate_extra = ""
    # if gradient and scatter dots
    if impact is not None and not show_impact_as_gradient:
        customdata_cols.append(col_color_impact)
        hovertemplate_extra = (
            f"<br>{col_color_impact.capitalize()}: %{{customdata[2]:.2f}}"
        )
    fig.add_choropleth(
        locations=df_hover_data["state_abbreviated"],
        locationmode="USA-states",
        customdata=df_hover_data[customdata_cols],
        z=df_hover_data[col_gradient],
        marker=dict(opacity=0),
        name="hover_info",
        hovertemplate=(
            "<b>%{customdata[0]}</b>"
            "<br>Sample size: %{customdata[1]}"
            f"<br>{col_gradient.capitalize()}: %{{z:.2f}}"
            f"{hovertemplate_extra}"
            "<extra></extra>"
        ),
        showscale=False,
    )

    # add dots for impact data
    if impact is not None and not show_impact_as_gradient:

        # add markers one at a time to control size
        for _, row in df_hover_data.iterrows():
            fig.add_scattergeo(
                locations=[row["state_abbreviated"]],
                locationmode="USA-states",
                text=[impact_emoji_map[impact]],
                mode="text",
                textfont={
                    "size": row[col_color_impact] * impact_marker_size_scale,
                },
                hoverinfo="skip",
                name="impact_scatter",
                showlegend=False,
            )

    # add state abbreviation labels
    fig.add_scattergeo(
        locations=state_abbrevs_long["state_abbreviated"],
        locationmode="USA-states",
        text=[
            f"<b>{abbr}</b>"
            for abbr in state_abbrevs_long["state_abbreviated"]
        ],
        mode="text",
        hoverinfo="skip",
        name="abbr_labels",
        showlegend=False,
    )

    # do not show base map
    fig.update_geos(visible=False)

    # zoom in to the US and adjust margins
    fig.update_layout(
        geo_scope="usa",
        margin=margins,
    )

    return fig


# if __name__ == "__main__":

#     import numpy as np

#     # pick a random state/cluster to highlight
#     states = state_abbreviations["state"].tolist()
#     clicked_state = np.random.choice(states)
#     # clicked_state = "Colorado, New Mexico (Cluster E)"  # example cluster
#     print(f"clicked_state: {clicked_state}")

#     fig = make_map(
#         question="q9b",
#         sub_question="1",
#         outcome="3+",
#         clicked_state=clicked_state,
#         # impact="tornado",
#         show_impact_as_gradient=True,
#     )

#     fig.show()
