import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import DATA_DICTIONARIES, GEOJSON_OBJECTS, SURVEY_DATA

survey_states = GEOJSON_OBJECTS["survey_states.json"]

opinions_state = SURVEY_DATA["opinions_state.tsv"]
samplesizes_state = SURVEY_DATA["samplesizes_state.tsv"]
sampledesc_state = SURVEY_DATA["sampledesc_state.tsv"]

impacts_state = SURVEY_DATA["impacts_state.tsv"]

state_abbreviations = DATA_DICTIONARIES["state_abbreviations.tsv"]


def get_state_abbrevs_in_long_format(state_abbreviations=state_abbreviations):
    # put the state abbreviations in a format where there's one row per state
    # i.e., flatten out the clusters
    # but still keep the "state" column as the original state/cluster name
    states = []
    single_states = []
    abbrevs = []
    for _, row in state_abbreviations.iterrows():
        state_list = row["state"].split(" (")[0].split(", ")
        single_states.extend(state_list)
        abbrev_list = row["state_abbreviated"].split(", ")
        abbrevs.extend(iter(abbrev_list))
        states.extend([row["state"]] * len(state_list))
    state_abbrevs_long = pd.DataFrame(
        data=np.array([states, single_states, abbrevs]).T,
        columns=["state", "single_state", "state_abbreviated"],
    )
    return state_abbrevs_long


def get_clusters(state_abbreviations=state_abbreviations):
    clusters = {}
    # get the clusters of states from the state abbreviations tsv
    for _, row in state_abbreviations.iterrows():
        if "Cluster" in row["state"]:
            i_and = row["state"].rfind(",") + 1
            cluster_name = row["state"][:i_and] + " and" + row["state"][i_and:]
            clusters[cluster_name] = row["state_abbreviated"].split(", ")
    return clusters


def add_opinions_data(
    state_abbrevs_long,
    question,
    sub_question,
    outcome,
    opinions_state=opinions_state,
):
    # select data
    opinions_state = opinions_state[opinions_state.question == f"q{question}"]
    opinions_state = opinions_state[
        opinions_state.sub_question == str(sub_question)
    ]
    opinions_state = opinions_state[opinions_state.outcome == outcome]

    # add data to state_abbrevs_long
    for i_states, row_states in state_abbrevs_long.iterrows():
        for _, row_opinions in opinions_state.iterrows():
            if row_states["state"] in row_opinions.state:
                state_abbrevs_long.loc[i_states, "to_plot"] = (
                    row_opinions.percentage * 100
                )
                state_abbrevs_long.loc[i_states, "pop_up"] = row_opinions.state
    return state_abbrevs_long


def add_impacts_data(
    state_abbrevs_long,
    number_of_impacts,
    impacts_state=impacts_state,
):
    # select data
    impacts_state = impacts_state[
        impacts_state.num_impacts == number_of_impacts
    ]

    # add data to state_abbrevs_long
    for i_states, row_states in state_abbrevs_long.iterrows():
        for _, row_impacts in impacts_state.iterrows():
            if row_states["state"] in row_impacts.state:
                state_abbrevs_long.loc[i_states, "to_plot"] = (
                    row_impacts.percentage * 100
                )
                state_abbrevs_long.loc[i_states, "pop_up"] = row_impacts.state
    return state_abbrevs_long


def make_base_map(state_abbrevs_long, colormap="Viridis"):
    # make map
    fig = go.Figure()
    fig.add_trace(
        go.Choropleth(
            locations=state_abbrevs_long["state_abbreviated"],
            z=state_abbrevs_long["to_plot"],
            zmax=state_abbrevs_long["to_plot"].max(),
            zmin=state_abbrevs_long["to_plot"].min(),
            locationmode="USA-states",
            colorscale=colormap,
            colorbar_title="Percentage",
            hovertext=state_abbrevs_long["pop_up"],
        )
    )
    # add state abbreviations to map
    fig.add_scattergeo(
        locations=state_abbrevs_long["state_abbreviated"],
        locationmode="USA-states",
        text=state_abbrevs_long["state_abbreviated"],
        mode="text",
    )
    # make it zoom onto the USA to start
    fig.update_layout(
        geo_scope="usa",
    )
    return fig


def outline_clicked_state(
    clicked_state, state_abbrevs_long, fig, colormap="Viridis"
):
    if clicked_state:
        # subset and text if there's only one state (it's not in a cluster)
        subset = state_abbrevs_long[
            state_abbrevs_long["state_abbreviated"] == clicked_state
        ]
        text = f"You're looking at data for {clicked_state}"

        # get subset and text if the state is in a cluster
        clusters = get_clusters()
        for cluster, states in clusters.items():
            if clicked_state in states:
                subset = state_abbrevs_long[
                    state_abbrevs_long["state_abbreviated"].isin(states)
                ]
                text = f"You're looking at data for {cluster}"

        # outline the state
        fig.add_trace(
            go.Choropleth(
                locations=subset["state_abbreviated"],
                z=subset["to_plot"],
                zmax=state_abbrevs_long["to_plot"].max(),
                zmin=state_abbrevs_long["to_plot"].min(),
                locationmode="USA-states",
                colorscale=colormap,
                colorbar_title="Percentage",
                hovertext=subset["pop_up"],
                marker=dict(line=dict(width=4, color="yellow")),
                colorbar=None,
            )
        )

        # add title under the map
        fig.update_layout(
            title_text=text,
            title_font_size=18,
            title_x=0.5,
            title_y=0.05,
            title_xanchor="center",
            geo_scope="usa",
        )
    return fig


def make_map():
    # user input
    outcome = "3+"
    question = 2
    sub_question = 1
    clicked_state = "NE"
    opinions_or_impacts = "opinions"
    number_of_impacts = 4
    colormap = "Viridis"

    # do the things
    state_abbrevs_long = get_state_abbrevs_in_long_format()
    if opinions_or_impacts == "opinions":
        state_abbrevs_long = add_opinions_data(
            state_abbrevs_long,
            question,
            sub_question,
            outcome,
        )
    if opinions_or_impacts == "impacts":
        state_abbrevs_long = add_impacts_data(
            state_abbrevs_long, number_of_impacts
        )
    fig = make_base_map(state_abbrevs_long, colormap)
    fig = outline_clicked_state(
        clicked_state, state_abbrevs_long, fig, colormap
    )
    fig.show()


def make_map2(
    question: str,
    sub_question: int,
    outcome: str,
    clicked_state: str,
    impact: str | None = None,
    show_impact_as_gradient=True,
    opinion_colormap: str | None = None,
    impact_colormap: str | None = "OrRd",
    clicked_state_marker: dict | None = None,
):
    # constants
    col_location = "state"
    col_color = "percentage"
    col_color_opinion = f"{col_color} (opinion)"
    col_color_impact = f"{col_color} (impact)"

    # default values
    if clicked_state_marker is None:
        clicked_state_marker = dict(line=dict(width=4, color="yellow"))

    # get the state abbreviations in long format
    # "state" (i.e. state or cluster), "single_state", "state_abbreviated"
    state_abbrevs_long = get_state_abbrevs_in_long_format()

    # get the question data
    df_opinions = opinions_state.loc[
        (opinions_state["question"] == question)
        & (opinions_state["sub_question"] == str(sub_question))
        & (opinions_state["outcome"] == outcome)
    ]

    if len(df_opinions) == 0:
        raise RuntimeError(
            f"No data found for question {question} ({type(question)})"
            f", sub_question {sub_question} ({type(sub_question)})"
            f", outcome {outcome} ({type(outcome)})"
        )

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
    vmin = df_to_plot[col_gradient].min()
    vmax = df_to_plot[col_gradient].max()

    # initialize the figure
    fig = go.Figure()

    # plot the question data on a map
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
    df_to_plot_clicked = df_to_plot[df_to_plot[col_location] == clicked_state]
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
        vmin_impact = df_hover_data[col_color_impact].min()
        vmax_impact = df_hover_data[col_color_impact].max()

        # add dots one at a time to control color/size
        for _, row in df_hover_data.iterrows():
            fig.add_scattergeo(
                locations=[row["state_abbreviated"]],
                locationmode="USA-states",
                marker={
                    "size": row[col_color_impact],
                    "color": px.colors.sample_colorscale(
                        impact_colormap,
                        (row[col_color_impact] - vmin_impact)
                        / (vmax_impact - vmin_impact),
                    ),
                },
                hoverinfo="skip",
                name="impact_scatter",
                mode="markers",
                showlegend=False,
            )

    # add state abbreviation labels
    fig.add_scattergeo(
        locations=state_abbrevs_long["state_abbreviated"],
        locationmode="USA-states",
        text=state_abbrevs_long["state_abbreviated"],
        mode="text",
        hoverinfo="skip",
        name="abbr_labels",
        showlegend=False,
    )

    # do not show base map
    fig.update_geos(visible=False)

    # zoom in to the US
    fig.update_layout(
        geo_scope="usa",
    )

    return fig


if __name__ == "__main__":
    # # old function
    # make_map()

    # pick a random state/cluster to highlight
    states = state_abbreviations["state"].tolist()
    clicked_state = np.random.choice(states)
    # clicked_state = "Colorado, New Mexico (Cluster E)"  # example cluster
    print(f"clicked_state: {clicked_state}")

    fig = make_map2(
        question="q2",
        sub_question=1,
        outcome="3+",
        clicked_state=clicked_state,
        impact="wildfire",
        show_impact_as_gradient=False,
    )

    fig.show()
