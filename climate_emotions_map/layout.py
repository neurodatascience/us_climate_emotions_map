"""Generate the layout for the dashboard."""

import dash_mantine_components as dmc

from . import utility as utils


def create_state_dropdown():
    """Create the dropdown for states and state clusters."""
    return dmc.Select(
        label="Select a state",
        placeholder="Showing national results",
        data=utils.get_state_options(),
        clearable=True,
        searchable=True,
        nothingFoundMessage="No matches",
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
                                children=[
                                    create_state_dropdown(),
                                ],
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
        children=[create_header()],
    )
