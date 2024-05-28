"""Main file to run the Dash app."""

import os

import dash_mantine_components as dmc
from dash import Dash, Input, Output, callback, _dash_renderer

from .data_loader import NATIONAL_SAMPLE_SIZE, SURVEY_DATA
from .layout import construct_layout

# Currently needed by DMC, https://www.dash-mantine-components.com/getting-started#simple-usage
_dash_renderer._set_react_version('18.2.0')

app = Dash(
    __name__,
    title="US Climate Emotions Map",
)

app.layout = dmc.MantineProvider(construct_layout(), forceColorScheme="light")

server = app.server


@callback(
    Output("drawer", "opened"),
    Input("drawer-button", "n_clicks"),
    prevent_initial_call=True,
)
def drawer_demo(n_clicks):
    """Callback function for toggling drawer visibility."""
    return True


@callback(
    Output("drawer-state", "children"),
    Input("state-select", "value"),
)
def update_drawer_state(value):
    """Callback function for updating the state in the drawer."""
    if value is None:
        return "National"
    return f"State: {value}"


@callback(
    Output("drawer-sample-size", "children"),
    [Input("state-select", "value")],
)
def updater_drawer_sample_size(value):
    """Callback function for updating the sample size in the drawer."""
    df = SURVEY_DATA["samplesizes_state.tsv"]
    if value is None:
        return f"Sample size: {NATIONAL_SAMPLE_SIZE}"
    return f"Sample size: {df[df['state'] == value]['n'].values[0]}"


if __name__ == "__main__":
    app.run(debug=True)
