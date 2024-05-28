"""
Load survey data and data dictionaries into dataframes.

Example usage: After importing SURVEY_DATA in another script, the dataframe for the
opinions_party.tsv data file can be accessed with SURVEY_DATA["opinions_party.tsv"].
"""

import json
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


def remove_ignored_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows from a dataframe that have a value of TRUE in the "ignore" column."""
    return df[df["ignore"] == False]


def load_geojson_object(file: str) -> dict:
    """Load a geojson file into a dataframe."""
    return json.loads(
        (Path(__file__).parents[1] / "code" / "assets" / file).read_text(),
    )


def load_survey_data() -> dict[str, pd.DataFrame]:
    """
    Load all survey result TSV files of interest.
    Climate impact data is excluded because it is not used in the dashboard.
    """
    data_files = [
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
        if "ignore" in data_frames[file].columns:
            data_frames[file] = remove_ignored_rows(data_frames[file])

    return data_frames


def load_geojson_objects() -> dict:
    """Load the available GeoJSON files."""
    geojson_files = [
        "us_states.json",
        "survey_states.json",
    ]
    geojson_objects = {}
    for file in geojson_files:
        geojson_objects[file] = load_geojson_object(file)
    return geojson_objects


SURVEY_DATA = load_survey_data()
# NOTE: column dtypes for opinions data TSVs
# Input:
# df = SURVEY_DATA["opinions_wholesample.tsv"]
# print(df.dtypes)
#
# Output:
# question         object
# sub_question     object
# outcome          object
# percentage      float64
# dtype: object

DATA_DICTIONARIES = load_data_dictionaries()
# NOTE: column dtypes for data dictionary TSVs
# Input:
# df = DATA_DICTIONARIES["subquestion_dictionary.tsv"]
# print(df.dtypes)
#
# Output:
# question        object
# sub_question    object
# full_text       object
# ignore            bool
# dtype: object

NATIONAL_SAMPLE_SIZE = SURVEY_DATA["samplesizes_state.tsv"]["n"].sum()
GEOJSON_OBJECTS = load_geojson_objects()
