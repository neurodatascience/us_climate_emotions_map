#!/usr/bin/env python

import pickle as pkl
import sys
from pathlib import Path

# Hacky hacky gets the job done for the next import
sys.path.append(str(Path(__file__).parent.parent))

from climate_emotions_map.make_stacked_bar_plots import (  # noqa
    DATA_DICTIONARIES,
    make_stacked_bar,
)

unique_questions_list = (
    DATA_DICTIONARIES["question_dictionary.tsv"]["question"].unique().tolist()
)
unique_states_list = (
    DATA_DICTIONARIES["state_abbreviations.tsv"]["state"].unique().tolist()
)


def make_full_set_of_barplots(state=None, stratify=None, threshold=None):
    """
    This returns a dictionary keyed on the question
    with the value being the plotly graph object figure for that question.
    """
    return {
        question: make_stacked_bar(question, "all", state, stratify, threshold)
        for question in unique_questions_list
    }


def make_all_figures():
    """
    Iterate through all combinations of questions and states
    to create the complete set of figures.

    Returns a dictionary keyed on the tuple of (state, stratified, threshold) in that order
    """
    figures = {}
    # A state of None means we are looking at national level questions
    for state in unique_states_list + [None]:
        for stratify in [False, True]:
            # For state level figures, we don't stratify by party
            if state is not None and stratify:
                continue
            for threshold in [None, "3+"]:
                key = (state, stratify, threshold)
                figures[key] = make_full_set_of_barplots(*key)
    return figures


if __name__ == "__main__":
    figures = make_all_figures()
    with open("prerendered_figures.pkl", "wb") as f:
        pkl.dump(figures, f)
