"""Main file to run the Dash app."""

import os

import dash_mantine_components as dmc
from dash import Dash, Input, Output, callback, ctx, no_update
from dash.exceptions import PreventUpdate

from .data_loader import NATIONAL_SAMPLE_SIZE, SURVEY_DATA
from .layout import construct_layout

# Currently needed by DMC, https://www.dash-mantine-components.com/getting-started#simple-usage
os.environ["REACT_VERSION"] = "18.2.0"

app = Dash(
    __name__,
    title="US Climate Emotions Map",
)

app.layout = dmc.MantineProvider(construct_layout(), forceColorScheme="light")

server = app.server


@callback(
    [
        Output("state-select", "value"),
        Output("state-select", "disabled"),
        Output("party-stratify-switch", "checked"),
        Output("party-stratify-switch", "disabled"),
    ],
    [
        Input("party-stratify-switch", "checked"),
        Input("state-select", "value"),
    ],
    prevent_initial_call=True,
)
def disable_state_select_and_party_switch_interaction(
    is_party_stratify_checked, selected_state
):
    """
    Disable the state dropdown when the party stratify switch is checked,
    and disable the party stratify switch when a specific state is selected (i.e., not None).
    """
    if ctx.triggered_id == "party-stratify-switch":
        # Deselect any state
        return None, is_party_stratify_checked, no_update, no_update
    if ctx.triggered_id == "state-select":
        if selected_state is not None:
            return no_update, no_update, False, True
        return no_update, no_update, False, False
    return PreventUpdate


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
