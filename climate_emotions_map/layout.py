"""Generate the layout for the dashboard."""

import dash_mantine_components as dmc
from dash import dcc

from . import utility as utils
from .make_descriptive_plots import make_descriptive_plots
from .make_map import make_map
from .make_stacked_bar_plots import make_stacked_bar
from .utility import (  # IMPACT_COLORMAP,; OPINION_COLORMAP,
    DEFAULT_MAP_TITLE,
    DEFAULT_QUESTION,
)


def create_question_dropdown():
    """
    Create the dropdown for subquestions grouped by question.
    NOTE: 'value' must be a string for DMC, so we use f-strings to concatenate the question and subquestion.
    """
    return dmc.Select(
        id="question-select",
        label="Select a question",  # "Select a sub-question"?
        data=utils.get_question_options(),
        value=f"{DEFAULT_QUESTION['question']}_{DEFAULT_QUESTION['sub_question']}",
        allowDeselect=False,
        clearable=False,
        searchable=True,
        nothingFoundMessage="No matches",
        styles={
            "group": {"marginTop": 10},
            "option": {"paddingTop": 2, "paddingBottom": 2},
            "input": {"textOverflow": "ellipsis"},
        },
    )


def create_state_dropdown():
    """Create the dropdown for states and state clusters."""
    return dmc.Select(
        id="state-select",
        label="Select a state",
        placeholder="Showing national results",
        data=utils.get_state_options(),
        clearable=True,
        searchable=True,
        nothingFoundMessage="No matches",
    )


def create_barplot_options_heading():
    label = dmc.Text("Bar chart options", size="sm", fw=500)
    return label


def create_party_switch():
    """Create the switch for stratifying data by party affiliation."""
    return dmc.Switch(
        id="party-stratify-switch",
        label="Stratify by party affiliation",
        checked=False,
    )


def create_response_threshold_control():
    """Create the switch that controls whether to binarize the response data (in stacked bar plots) by an endorsement threshold."""
    return dmc.Switch(
        id="response-threshold-control",
        label="Show all endorsement levels",
        checked=False,
    )


def create_drawer_state():
    """Create the state/cluster for the drawer."""
    return dmc.Text(id="drawer-state", size="md")


def create_drawer_sample_size():
    """Create the sample size for the drawer."""
    return dmc.Text(id="drawer-sample-size", size="md")


def create_sample_descriptive_plot():
    """Create the component holding the subplots of sample descriptive statistics."""
    return dcc.Graph(
        id="sample-descriptive-plot",
        figure=make_descriptive_plots(
            state=None,
        ),
        # TODO: Revisit once we've made plot margins smaller (or create a param for this, maybe)
        # TODO: Fix margins to prevent text from being cut off; make kwargs work
        style={"height": "90vh"},
    )


def create_sample_description_drawer():
    """Create the toggleable drawer for sample description."""
    # TODO: Make drawer slide in faster, and remove trap focus (?) so that user can interact with rest of app
    # TODO: Make "View Sample Description" button also able to close the drawer
    return dmc.Container(
        [
            dmc.Button(
                "View Sample Description", id="drawer-button", variant="subtle"
            ),
            dmc.Drawer(
                children=[
                    create_drawer_state(),
                    create_drawer_sample_size(),
                    create_sample_descriptive_plot(),
                ],
                title=dmc.Title("Sample Description", order=3, fw=300),
                id="drawer",
                padding="md",
                transitionProps={
                    "transition": "slide-left",
                    "duration": 550,
                    "timingFunction": "ease",
                },
                # TODO: Revisit size once plot margins are adjusted
                size="30%",
                position="right",
                # Allow user to interact with content in rest of the app when the drawer is open
                withOverlay=False,
            ),
        ]
    )


def create_navbar():
    """Create the navbar for the dashboard."""
    return dmc.AppShellNavbar(
        children=dmc.Stack(
            mt=25,
            px=25,
            gap="lg",
            children=[
                create_question_dropdown(),
                create_state_dropdown(),
                create_barplot_options_heading(),
                create_party_switch(),
                create_response_threshold_control(),
                create_sample_description_drawer(),
            ],
        )
    )


def create_header():
    """Create the header for the dashboard."""
    return dmc.AppShellHeader(
        # See https://www.dash-mantine-components.com/style-props
        px=25,
        children=[
            dmc.Stack(
                justify="center",
                h=70,
                children=dmc.Grid(
                    justify="space-between",
                    align="center",
                    children=[
                        dmc.GridCol(
                            children=dmc.Anchor(
                                "US Climate Emotions Map 2024",
                                size="xl",
                                href="/",
                                underline=False,
                            ),
                            span="content",
                        ),
                        dmc.GridCol(
                            dmc.Group(
                                justify="flex-end",
                                # TODO: Add GitHub link? Not sure if needed/wanted.
                                # TODO: Add link to paper
                            ),
                            span="auto",
                        ),
                    ],
                ),
            )
        ],
    )


def create_question_title():
    """Create the title for the main content of the dashboard."""
    return dmc.Stack(
        children=[
            dmc.Title(
                id="map-title",
                children=DEFAULT_MAP_TITLE,
                order=3,
                fw=300,
            ),
            dmc.Text(
                id="map-subtitle",
                children=utils.create_question_subtitle(
                    question=DEFAULT_QUESTION["question"],
                    subquestion=DEFAULT_QUESTION["sub_question"],
                ),
                size="lg",
            ),
        ],
        gap="0",
    )


def create_impact_dropdown():
    """Create the dropdown for selecting the impact to display."""
    return dmc.Flex(
        dmc.Select(
            id="impact-select",
            label="View distribution of self-reported severe weather event",
            placeholder="Select a severe weather event",
            data=utils.get_impact_options(),
            clearable=True,
            searchable=True,
            nothingFoundMessage="No matches",
        ),
        justify="flex-end",
    )


def create_map_plot():
    """Create the component holding the cloropleth map plot of US states."""
    # TODO: Ensure that state click events are handled properly
    us_map = dmc.Container(
        # TODO: Make map margins smaller (or create a param for this, maybe), and make figure height larger (?)
        dcc.Graph(
            id="us-map",
            figure=make_map(
                question=DEFAULT_QUESTION["question"],
                sub_question=DEFAULT_QUESTION["sub_question"],
                outcome=DEFAULT_QUESTION["outcome"],
                # opinion_colormap=OPINION_COLORMAP,
            ),
            # vh = % of viewport height
            # TODO: Revisit once plot margins are adjusted
            style={"height": "65vh"},
        ),
        # sets max width
        # TODO: Revisit once plot margins are adjusted
        size="lg",
    )
    return us_map


def create_stacked_bar_plots():
    """Create component to hold the stacked bar plot(s) for a subquestion."""
    figure = dmc.Container(
        dcc.Graph(
            id="stacked-bar-plot",
            figure=make_stacked_bar(
                question=DEFAULT_QUESTION["question"],
                subquestion=DEFAULT_QUESTION["sub_question"],
                state=None,
                stratify=False,
                threshold=DEFAULT_QUESTION["outcome"],
                binarize_threshold=True,
            ),
            style={"height": "20vh"},
        ),
        size="xl",
    )
    return figure


def create_main():
    """Create the main content of the dashboard."""
    return dmc.AppShellMain(
        children=[
            dmc.Container(
                my=25,
                mx="xs",
                fluid=True,
                children=[
                    create_question_title(),
                    create_impact_dropdown(),
                    create_map_plot(),
                    create_stacked_bar_plots(),
                ],
            )
        ]
    )


def construct_layout():
    """Generate the overall dashboard layout."""
    return dmc.AppShell(
        children=[create_header(), create_navbar(), create_main()],
        header={"height": 70},
        navbar={"width": 400},
    )
