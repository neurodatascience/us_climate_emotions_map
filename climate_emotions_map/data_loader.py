"""
Load survey data and data dictionaries into dataframes.

Example usage: After importing SURVEY_DATA in another script, the dataframe for the
opinions_party.tsv data file can be accessed with SURVEY_DATA["opinions_party.tsv"].
"""

from pathlib import Path

import pandas as pd


def load_data_file(file: str) -> pd.DataFrame:
    """Load a TSV data file into a dataframe."""
    return pd.read_csv(
        Path(__file__).parents[1] / "data" / "survey_results" / file, sep="\t"
    )


def load_data_dictionary(file: str) -> pd.DataFrame:
    """Load a data dictionary TSV into a dataframe."""
    return pd.read_csv(
        Path(__file__).parents[1] / "data" / "data_dictionaries" / file,
        sep="\t",
    )


def load_survey_data() -> dict[str, pd.DataFrame]:
    """
    Load all survey result TSV files of interest.
    Climate impact data is excluded because it is not used in the dashboard.
    """
    data_files = [
        "impacts_state.tsv",
        "opinions_party.tsv",
        "opinions_state.tsv",
        "opinions_wholesample.tsv",
        "sampledesc_state.tsv",
        "sampledesc_wholesample.tsv",
        "samplesizes_party.tsv",
        "samplesizes_state.tsv",
    ]

    data_frames = {}
    for file in data_files:
        data_frames[file] = load_data_file(file)

    return data_frames


def load_data_dictionaries() -> dict[str, pd.DataFrame]:
    """Load the data dictionaries for the survey data."""
    data_files = [
        "impacts_list.tsv",
        "outcome_dictionary.tsv",
        "question_dictionary.tsv",
        "state_abbreviations.tsv",
        "subquestion_dictionary.tsv",
    ]

    data_frames = {}
    for file in data_files:
        data_frames[file] = load_data_dictionary(file)

    return data_frames


SURVEY_DATA = load_survey_data()
DATA_DICTIONARIES = load_data_dictionaries()
