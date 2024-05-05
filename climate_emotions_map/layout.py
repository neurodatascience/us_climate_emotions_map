"""Generate the layout for the dashboard."""

import dash_mantine_components as dmc

from . import utility as utils

DEFAULT_QUESTION = {"question": "q2", "sub_question": 1}


def create_question_dropdown():
    """Create the dropdown for subquestions grouped by question."""
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


def create_party_switch():
    """Create the switch for stratifying data by party affiliation."""
    return dmc.Switch(
        id="party-stratify-switch",
        label="Stratify by party affiliation",
        checked=False,
    )


def create_response_threshold_control():
    """Create the segmented control for selecting the endorsement threshold to display."""
    label = dmc.Text(
        "Display results for responses rated:", size="sm"
    )  # "response endorsements of"?

    segmented_control = dmc.SegmentedControl(
        id="response-threshold-control",
        data=[
            {"label": "Any endorsement level", "value": "all"},
            {"label": "3+ (moderately and above)", "value": "3+"},
            {"label": "4+ (very much and above)", "value": "4+"},
        ],
        orientation="vertical",
        fullWidth=True,
    )

    return dmc.Stack(
        gap=5,
        children=[label, segmented_control],
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
                create_party_switch(),
                create_response_threshold_control(),
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


def construct_layout():
    """Generate the overall dashboard layout."""
    return dmc.AppShell(
        children=[create_header(), create_navbar()],
        header={"height": 70},
        navbar={"width": 400},
    )
