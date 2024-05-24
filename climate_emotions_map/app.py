"""Main file to run the Dash app."""

import os

import dash_mantine_components as dmc
from dash import Dash, Input, Output, callback, ctx, no_update
from dash.exceptions import PreventUpdate

from . import utility as utils
from .data_loader import NATIONAL_SAMPLE_SIZE, SURVEY_DATA
from .layout import construct_layout
from .make_map import make_map
from .utility import (
    DEFAULT_QUESTION,
    NO_THRESHOLD_OPTION_VALUE,
    OPINION_COLORMAP,
)

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
    raise PreventUpdate


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
def update_drawer_sample_size(value):
    """Callback function for updating the sample size in the drawer."""
    df = SURVEY_DATA["samplesizes_state.tsv"]
    if value is None:
        return f"Sample size: {NATIONAL_SAMPLE_SIZE}"
    return f"Sample size: {df[df['state'] == value]['n'].values[0]}"


@callback(
    Output("map-title", "children"),
    Input("response-threshold-control", "value"),
)
def update_map_title(threshold):
    """Update the map title based on the selected threshold."""
    # TODO: Revisit if we want to fix the threshold for the opinion data for the map
    if threshold == NO_THRESHOLD_OPTION_VALUE:
        raise PreventUpdate
    return utils.create_map_title(threshold)


@callback(
    Output("map-subtitle", "children"),
    Input("question-select", "value"),
)
def update_map_subtitle(question_value):
    """Update the map subtitle based on the selected question."""
    question, subquestion = utils.extract_question_subquestion(question_value)
    return utils.create_question_subtitle(question, subquestion)


@callback(
    Output("us-map", "figure"),
    [
        Input("question-select", "value"),
        Input("response-threshold-control", "value"),
    ],
    prevent_initial_call=True,
)
def update_map_opinion_data(question_value, threshold):
    """
    Update the map with the opinion data for the selected question (value encodes a question-subquestion pairing)
    and response threshold, if a threshold is selected.
    """
    question, subquestion = utils.extract_question_subquestion(question_value)
    if threshold != NO_THRESHOLD_OPTION_VALUE:
        figure = make_map(
            question=question,
            sub_question=subquestion,
            outcome=threshold,
            opinion_colormap=OPINION_COLORMAP,
        )
        return figure
    raise PreventUpdate


@callback(
    Output("response-threshold-control", "value"),
    [
        Input("question-select", "value"),
        Input("response-threshold-control", "value"),
    ],
    prevent_initial_call=True,
)
def reset_response_threshold_control(question_value, threshold):
    """
    Reset the response threshold to the default threshold when a new question is selected
    AND the currently selected threshold is the option to show all Likert responses (i.e., no threshold).

    # TODO: Revisit if we want this, or if the map should always show 3+ data.
    # One downside is that if a user wants to see stacked bars with all responses,
    # they would have to re-select 'no threshold' every time after switching questions.
    """
    if (
        ctx.triggered_id == "question-select"
        and threshold == NO_THRESHOLD_OPTION_VALUE
    ):
        return DEFAULT_QUESTION["outcome"]
    raise PreventUpdate


if __name__ == "__main__":
    app.run(debug=True)
