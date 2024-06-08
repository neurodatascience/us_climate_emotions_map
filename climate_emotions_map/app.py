"""Main file to run the Dash app."""

import dash_mantine_components as dmc
from dash import (
    ALL,
    Dash,
    Input,
    Output,
    State,
    _dash_renderer,
    callback,
    ctx,
    no_update,
)
from dash.exceptions import PreventUpdate

from . import utility as utils
from .data_loader import NATIONAL_SAMPLE_SIZE, SURVEY_DATA
from .layout import MAP_LAYOUT, SINGLE_SUBQUESTION_FIG_KW, construct_layout
from .make_descriptive_plots import make_descriptive_plots
from .make_map import make_map
from .make_stacked_bar_plots import make_stacked_bar
from .utility import (  # IMPACT_COLORMAP,; OPINION_COLORMAP,
    ALL_STATES_LABEL,
    DEFAULT_QUESTION,
    SECTION_TITLES,
)

# Currently needed by DMC, https://www.dash-mantine-components.com/getting-started#simple-usage
_dash_renderer._set_react_version("18.2.0")

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
        Input("us-map", "clickData"),
        Input("party-stratify-switch", "checked"),
        Input("state-select", "value"),
    ],
    prevent_initial_call=True,
)
def update_state_and_disable_state_select_and_party_switch_interaction(
    figure, is_party_stratify_checked, selected_state
):
    """
    Update the state dropdown when a specific state is clicked (if party stratify switch is not checked),
    disable the state dropdown when the party stratify switch is checked,
    and disable the party stratify switch when a specific state is selected (i.e., not None).
    """
    if ctx.triggered_id == "us-map":
        map_selected_state = figure["points"][0]["customdata"][0]

        if is_party_stratify_checked or map_selected_state == selected_state:
            raise PreventUpdate
        return (
            map_selected_state,
            no_update,
            False,
            True,
        )
    if ctx.triggered_id == "party-stratify-switch":
        # Deselect any state
        return None, is_party_stratify_checked, no_update, no_update

    if selected_state is not None:
        return no_update, no_update, False, True
    return no_update, no_update, False, False


@callback(
    Output("drawer", "opened"),
    Input("drawer-button", "n_clicks"),
    State("drawer", "opened"),
    prevent_initial_call=True,
)
def drawer_toggle(n_clicks, opened):
    """Callback function for toggling drawer visibility."""
    return not opened


@callback(
    Output("drawer-state", "children"),
    Input("state-select", "value"),
)
def update_drawer_state(value):
    """Callback function for updating the state in the drawer."""
    if value is None:
        return ALL_STATES_LABEL
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
    Output("sample-descriptive-plot", "figure"),
    Input("state-select", "value"),
    prevent_initial_call=True,
)
def update_sample_descriptive_plot(state):
    """Update the sample descriptive plot based on the selected state."""
    return make_descriptive_plots(
        state=state,
    )


@callback(
    Output("impact-select", "value"),
    Input("question-select", "value"),
)
def reset_impact_select(question_value):
    """Reset the impact select dropdown when a new question is selected."""
    return None


@callback(
    Output("map-title", "children"),
    Input("impact-select", "value"),
    State("impact-select", "data"),
    prevent_initial_call=True,
)
def update_map_title(impact, options):
    """Update the map title when a specific impact is selected (or if the selection is cleared)."""
    label = next(
        (option["label"] for option in options if option["value"] == impact),
        None,
    )
    return utils.create_map_title(label)


@callback(
    Output("map-subtitle", "children"),
    [
        Input("question-select", "value"),
        Input("impact-select", "value"),
    ],
)
def update_map_subtitle(question_value, impact):
    """Update the map subtitle based on the selected question and whether an impact is selected."""
    if impact is not None:
        return ""

    question, subquestion = utils.extract_question_subquestion(question_value)
    return utils.create_question_subtitle(question, subquestion)


@callback(
    Output("us-map", "figure"),
    [
        Input("question-select", "value"),
        Input("state-select", "value"),
        Input("impact-select", "value"),
    ],
    prevent_initial_call=True,
)
def update_map(question_value, state, impact):
    """
    Update the map with the opinion data for the selected question (value encodes a question-subquestion pairing)
    at the set default threshold.

    Also updates the map with the impact data if a specific impact is selected.
    """
    question, subquestion = utils.extract_question_subquestion(question_value)

    return make_map(
        question=question,
        sub_question=subquestion,
        outcome=DEFAULT_QUESTION["outcome"],
        clicked_state=state,
        impact=impact,
        colormap_range_padding=MAP_LAYOUT["colormap_range_padding"],
        margins=MAP_LAYOUT["margin"],
        # opinion_colormap=OPINION_COLORMAP,
        # impact_colormap=IMPACT_COLORMAP,
    )


@callback(
    Output("selected-question-bar-plot", "figure"),
    [
        Input("question-select", "value"),
        Input("state-select", "value"),
        Input("party-stratify-switch", "checked"),
        Input("response-threshold-control", "checked"),
    ],
    prevent_initial_call=True,
)
def update_selected_question_bar_plot(
    question_value,
    state,
    is_party_stratify_checked,
    show_all_responses_checked,
):
    """Update the stacked bar plot for the selected question based on the selected criteria."""
    question, subquestion = utils.extract_question_subquestion(question_value)

    if show_all_responses_checked:
        threshold = None
    elif not show_all_responses_checked:
        threshold = DEFAULT_QUESTION["outcome"]

    figure = make_stacked_bar(
        question=question,
        subquestion=subquestion,
        state=state,
        stratify=is_party_stratify_checked,
        threshold=threshold,
        fig_kw=SINGLE_SUBQUESTION_FIG_KW,
    )
    return figure


@callback(
    Output("selected-question-title", "children"),
    Input("state-select", "value"),
    prevent_initial_call=True,
)
def update_selected_question_title(state):
    """Update the title for the selected question based on the selected state."""
    if state is None:
        return f"{SECTION_TITLES['selected_question']}, {ALL_STATES_LABEL}"
    return f"{SECTION_TITLES['selected_question']}, {state}"


@callback(
    Output("selected-question-container", "display"),
    Input("impact-select", "value"),
    prevent_initial_call=True,
)
def toggle_selected_question_bar_plot_visibility(impact):
    """Toggle visibility of the selected question bar plot component based on whether an impact is selected."""
    if impact is not None:
        return "none"
    return "flex"


@callback(
    Output("all-questions-title", "children"),
    Input("state-select", "value"),
)
def update_all_questions_title(state):
    """Update the title for the section for all questions based on the selected state."""
    if state is None:
        return f"{SECTION_TITLES['all_questions']}, {ALL_STATES_LABEL}"
    return f"{SECTION_TITLES['all_questions']}, {state}"


@callback(
    Output({"type": "stacked-bar-plot", "question": ALL}, "figure"),
    [
        Input("state-select", "value"),
        Input("party-stratify-switch", "checked"),
        Input("response-threshold-control", "checked"),
    ],
    prevent_initial_call=True,
)
def update_stacked_bar_plots(
    state,
    is_party_stratify_checked,
    show_all_responses_checked,
):
    """Update the stacked bar plots for all questions based on the selected criteria."""
    figures = []
    for output in ctx.outputs_list:
        # Example: {'id': {'question': 'q2', 'type': 'stacked-bar-plot'}, 'property': 'figure'}
        question = output["id"]["question"]

        if show_all_responses_checked:
            threshold = None
        elif not show_all_responses_checked:
            threshold = DEFAULT_QUESTION["outcome"]

        figure = make_stacked_bar(
            question=question,
            subquestion="all",
            state=state,
            stratify=is_party_stratify_checked,
            threshold=threshold,
        )
        figures.append(figure)

    return figures


if __name__ == "__main__":
    app.run(debug=True)
