"""Utility functions for the Climate Emotions Map app."""

from .data_loader import SURVEY_DATA


def get_state_options():
    """Get the options for the state dropdown."""
    # TODO: The state values include cluster labels in parentheses, e.g. (Cluster F). Can remove from label if desired.
    return [
        {"label": state, "value": state}
        for state in SURVEY_DATA["samplesizes_state.tsv"]["state"]
    ]
