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

UNIQUE_QUESTIONS = (
    DATA_DICTIONARIES["question_dictionary.tsv"]["question"].unique().tolist()
)
UNIQUE_STATES = (
    DATA_DICTIONARIES["state_abbreviations.tsv"]["state"].unique().tolist()
)
OUTPUT_FILE = Path(__file__).parents[0] / "assets/prerendered_figures.pkl"


def make_full_set_of_barplots(state=None, stratify=None, threshold=None):
    """
    This returns a dictionary for all questions where keys are question IDs
    and values are the plotly graph object figure for each question.
    """
    return {
        question: make_stacked_bar(question, "all", state, stratify, threshold, NUM_DECIMALS)
        for question in UNIQUE_QUESTIONS
    }


def make_all_figures():
    """
    Iterate through all combinations of questions and states
    to create the complete set of figures.

    Returns a dictionary keyed on the tuple of (state, stratified, threshold) in that order
    """
    figures = {}
    # A state of None means we are looking at national level questions
    for state in UNIQUE_STATES + [None]:
        for stratify in [False, True]:
            # For state level figures, we don't stratify by party
            if state is not None and stratify:
                continue
            for threshold in [None, DEFAULT_QUESTION["outcome"]]:
                key = (state, stratify, threshold)
                figures[key] = make_full_set_of_barplots(*key)
    return figures


if __name__ == "__main__":
    figures = make_all_figures()
    with OUTPUT_FILE.open("wb") as f:
        pkl.dump(figures, f)

    print(f"Done prerendering figures to {OUTPUT_FILE}!")
