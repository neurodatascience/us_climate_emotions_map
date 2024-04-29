from pathlib import Path

import pandas as pd


def load_data_file(file: str) -> pd.DataFrame:
    """
    Load the data from one TSV file into a dataframe.
    """
    return pd.read_csv(
        Path(__file__).parents[1] / "data" / "survey_results" / file, sep="\t"
    )


def load_survey_data():
    """
    Load all survey result TSV files into dataframes.
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


SURVEY_DATA = load_survey_data()
