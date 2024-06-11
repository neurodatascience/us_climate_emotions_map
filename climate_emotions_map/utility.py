"""Utility functions for the Climate Emotions Map app."""

from .data_loader import DATA_DICTIONARIES, SURVEY_DATA

DEFAULT_QUESTION = {
    "domain": "Climate emotions & beliefs",
    "question": "q2",
    "sub_question": "1",
    "outcome": "3+",
}
ALL_STATES_LABEL = "National"
SECTION_TITLES = {
    "app": "US Climate Emotions Map",
    "map_opinions": "Percent (%) of adolescents and young adults who endorse the following question/statement:",
    "map_impacts": "Map: Percent (%) of adolescents and young adults who reported experiencing the following in the last year",
    "selected_question": "Response distribution",
    "all_questions": "Climate emotions and thoughts of adolescents and young adults",
    "demographics": "Sample Characteristics",
}

# We have not yet decided on the best colormaps to use
# OPINION_COLORMAP = "OrRd"
# IMPACT_COLORMAP = "magma_r"


def get_state_options():
    """Get the options for the state dropdown."""
    return [
        {"label": state, "value": state}
        for state in SURVEY_DATA["samplesizes_state.tsv"]["state"]
    ]


def get_question_options():
    """Construct the data for the question dropdown, where each option is a subquestion and subquestions are grouped by question."""
    subquestions_grouped = DATA_DICTIONARIES[
        "subquestion_dictionary.tsv"
    ].groupby("question")

    data = []
    # TODO: Try to refactor this to not use iterrows
    for _, q_row in DATA_DICTIONARIES["question_dictionary.tsv"].iterrows():
        question = q_row["question"]
        question_label = q_row["dropdown_text"]

        group = subquestions_grouped.get_group(question)
        if group.shape[0] > 1:
            data_group = {"group": question_label, "items": []}
            for _, sq_row in group.iterrows():
                # NOTE: Option `value` must be a string for DMC.
                data_group["items"].append(
                    {
                        "label": sq_row["dropdown_text"],
                        "value": f"{question}_{sq_row['sub_question']}",
                    }
                )
        else:
            # If there is only one subquestion (meaning no subquestions),
            # create a group with an empty group label so it still receives the correct whitespace around it in the dropdown
            data_group = {
                "group": "",
                "items": [{"label": question_label, "value": f"{question}_1"}],
            }

        data.append(data_group)

    return data


def extract_question_subquestion(value: str) -> tuple[str, str]:
    """Extract the question and subquestion from a value in the question dropdown."""
    question, sub_question = value.split("_")
    return question, sub_question


def create_map_title(impact: str = None) -> str:
    """Create a statement for the map title based on whether a weather impact has been selected."""
    if impact is None:
        return SECTION_TITLES["map_opinions"]

    return f"{SECTION_TITLES['map_impacts']}: {impact}"


def create_question_subtitle(question: str, subquestion: str) -> str:
    """Get the full text to display for a question-subquestion pair as the subtitle for the map plot."""
    q_df = DATA_DICTIONARIES.get("question_dictionary.tsv")
    sq_df = DATA_DICTIONARIES.get("subquestion_dictionary.tsv")

    sq_text = sq_df.query(
        f'question=="{question}" & sub_question=="{subquestion}"'
    )["full_text"].values[0]
    if sq_df.query(f'question=="{question}"').shape[0] == 1:
        # If there is only one subquestion, return the subquestion text assuming it is the same as the question text
        return sq_text

    q_text = q_df.query(f'question=="{question}"')["full_text"].values[0]
    # TODO: Revisit format for long subquestions - add newline?
    return f'{q_text} "{sq_text}"'


def get_impact_options() -> list[dict]:
    """Get the options for the impact dropdown."""
    demog_df = DATA_DICTIONARIES["demographics_dictionary.tsv"]
    impact_df = DATA_DICTIONARIES["impacts_list.tsv"]

    # Get the impacts that are demographic questions
    filt_demog = demog_df[
        demog_df["demographic_variable"].isin(impact_df["impact"])
    ]
    options = filt_demog.rename(
        columns={"demographic_variable": "value", "full_text": "label"}
    ).to_dict(orient="records")

    return options
