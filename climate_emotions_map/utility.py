"""Utility functions for the Climate Emotions Map app."""

from .data_loader import DATA_DICTIONARIES, SURVEY_DATA


def get_state_options():
    """Get the options for the state dropdown."""
    # TODO: The state values include cluster labels in parentheses, e.g. (Cluster F). Can remove from label if desired.
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
    for _, q_row in DATA_DICTIONARIES["question_dictionary.tsv"].iterrows():
        question = q_row["question"]
        question_label = q_row["full_text"]

        group = subquestions_grouped.get_group(question)
        if group.shape[0] > 1:
            data_group = {"group": question_label, "items": []}
            for _, sq_row in group.iterrows():
                # NOTE: Option `value` must be a string for DMC.
                data_group["items"].append(
                    {
                        "label": sq_row["full_text"],
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
