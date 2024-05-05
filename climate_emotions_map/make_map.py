import numpy as np
import pandas as pd
import plotly.graph_objects as go
from data_loader import load_data_dictionaries, load_survey_data

opinions_state = load_survey_data()["opinions_state.tsv"]

impacts_state = load_survey_data()["impacts_state.tsv"]

state_abbreviations = load_data_dictionaries()["state_abbreviations.tsv"]


def get_state_abbrevs_in_long_format(state_abbreviations=state_abbreviations):
    # put the state abbreviations in a format where there's one row per state
    # i.e., flatten out the clusters
    states = []
    abbrevs = []
    for _, row in state_abbreviations.iterrows():
        state_list = row["state"].split(", ")
        states.extend(
            state.split("(")[0].replace("(", "") for state in state_list
        )
        abbrev_list = row["state_abbreviated"].split(", ")
        abbrevs.extend(iter(abbrev_list))
    state_abbrevs_long = pd.DataFrame(
        data=np.array([states, abbrevs]).T,
        columns=["state", "state_abbreviated"],
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


if __name__ == "__main__":
    make_map()
