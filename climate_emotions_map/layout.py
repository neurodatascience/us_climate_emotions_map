"""Generate the layout for the dashboard."""

import dash_mantine_components as dmc
import pandas as pd
from dash import dcc, html

from . import utility as utils
from .data_loader import DATA_DICTIONARIES, DOMAIN_TEXT
from .make_descriptive_plots import make_descriptive_plots
from .make_map import make_map
from .make_stacked_bar_plots import make_stacked_bar
from .utility import (  # IMPACT_COLORMAP,; OPINION_COLORMAP,
    DEFAULT_QUESTION,
    SECTION_TITLES,
)

HEADER_HEIGHT = 110
SINGLE_SUBQUESTION_FIG_KW = {
    "fontsize": 10,
    # NOTE: Can calculate same actual height as create_bar_plots_for_question with:
    # ( default height - (default-set margin top) - (default-set margin bottom) )
    "height": 105,
    "margin": {"l": 30, "r": 30, "t": 5, "b": 20},
}


def create_question_dropdown():
    """
    Create the dropdown for subquestions grouped by question.
    NOTE: 'value' must be a string for DMC, so we use f-strings to concatenate the question and subquestion.
    """
    return dmc.Select(
        id="question-select",
        label="Select a question",  # "Select a sub-question"?
        data=utils.get_question_options(),
        value=f"{DEFAULT_QUESTION['question']}_{DEFAULT_QUESTION['sub_question']}",
        allowDeselect=False,
        clearable=False,
        searchable=True,
        nothingFoundMessage="No matches",
        styles={
            "group": {"marginTop": 10},
            "option": {"paddingTop": 2, "paddingBottom": 2},
            "input": {"textOverflow": "ellipsis"},
        },
    )


def create_state_dropdown():
    """Create the dropdown for states and state clusters."""
    return dmc.Select(
        id="state-select",
        label="Select a state",
        placeholder="Showing national results",
        data=utils.get_state_options(),
        clearable=True,
        searchable=True,
        nothingFoundMessage="No matches",
    )


def create_barplot_options_heading():
    label = dmc.Text("Bar chart options", size="sm", fw=500)
    return label


def create_party_switch():
    """Create the switch for stratifying data by party affiliation."""
    return dmc.Switch(
        id="party-stratify-switch",
        label="Stratify by party affiliation",
        checked=False,
    )


def create_response_threshold_control():
    """Create the switch that controls whether to binarize the response data (in stacked bar plots) by an endorsement threshold."""
    return dmc.Switch(
        id="response-threshold-control",
        label="Show all endorsement levels",
        checked=False,
    )


def create_drawer_state():
    """Create the state/cluster for the drawer."""
    return dmc.Text(id="drawer-state", size="md")


def create_drawer_sample_size():
    """Create the sample size for the drawer."""
    return dmc.Text(id="drawer-sample-size", size="md")


def create_sample_descriptive_plot():
    """Create the component holding the subplots of sample descriptive statistics."""
    return dcc.Graph(
        id="sample-descriptive-plot",
        figure=make_descriptive_plots(
            state=None,
        ),
        # TODO: Revisit once we've made plot margins smaller (or create a param for this, maybe)
        # TODO: Fix margins to prevent text from being cut off; make kwargs work
        style={"height": "90vh"},
    )


def create_sample_description_drawer():
    """Create the toggleable drawer for sample description."""
    return dmc.Container(
        [
            dmc.Button(
                "View Sample Characteristics",
                id="drawer-button",
                variant="subtle",
            ),
            dmc.Drawer(
                children=[
                    create_drawer_state(),
                    create_drawer_sample_size(),
                    create_sample_descriptive_plot(),
                ],
                title=dmc.Title(
                    SECTION_TITLES["demographics"], order=3, fw=300
                ),
                id="drawer",
                padding="md",
                transitionProps={
                    "transition": "slide-left",
                    "duration": 375,
                    "timingFunction": "ease",
                },
                # TODO: Revisit size once plot margins are adjusted
                size="30%",
                position="right",
                # Allow user to interact with content in rest of the app when the drawer is open
                withOverlay=False,
                lockScroll=False,
            ),
        ]
    )


def create_design_credit():
    """Create the text hovercard for web app developer details."""
    short_credit = dmc.Text(
        children="Built by members of the ORIGAMI Lab",
        size="xs",
        c="dimmed",
    )

    long_credit = dmc.Text(
        children=[
            dmc.Text(
                "Alyssa Dai, Nikhil Bhagwat, Rémi Gau, Arman Jahanpour, Kendra Oudyk, Sebastian Urchs, Michelle Wang"
            ),
            dmc.Anchor(
                "ORIGAMI Lab, PI: Jean-Baptiste Poline",
                href="https://neurodatascience.github.io/",
                target="_blank",
            ),
        ],
        size="xs",
        c="dimmed",
    )

    return dmc.HoverCard(
        withArrow=True,
        width=350,
        offset=3,
        shadow="sm",
        children=[
            dmc.HoverCardTarget(children=short_credit),
            dmc.HoverCardDropdown(children=long_credit),
        ],
    )


def create_navbar():
    """Create the navbar for the dashboard."""
    return dmc.AppShellNavbar(
        children=dmc.Flex(
            mt=25,
            px=25,
            h="100vh",
            gap="lg",
            direction="column",
            children=[
                dmc.Stack(
                    children=[
                        create_question_dropdown(),
                        create_state_dropdown(),
                        create_barplot_options_heading(),
                        create_party_switch(),
                        create_response_threshold_control(),
                        create_sample_description_drawer(),
                    ],
                ),
                dmc.Container(
                    create_design_credit(),
                    mt="auto",
                    pb=25,
                ),
            ],
        ),
    )


def create_app_subtitle():
    """Create the subtitle for the dashboard."""
    return dmc.Text(
        children=[
            'Graphical appendix for "Climate emotions, thoughts, and plans among US adolescents and young adults" \n(Lewandowski, R.E, Clayton, S.D., Olbrich, L., Sakshaug, J.W., Wray, B. et al, (2024) ',
            html.I("Lancet Planetary Health, "),
            "(volume, issue, tbd)",
        ],
        size="sm",
        c="dimmed",
        style={"whiteSpace": "pre-wrap"},
    )


def create_header():
    """Create the header for the dashboard."""
    return dmc.AppShellHeader(
        # See https://www.dash-mantine-components.com/style-props
        px=25,
        children=[
            dmc.Stack(
                justify="center",
                h=HEADER_HEIGHT,
                children=dmc.Grid(
                    justify="space-between",
                    align="center",
                    children=[
                        dmc.GridCol(
                            children=dmc.Stack(
                                gap=5,
                                justify="center",
                                children=[
                                    dmc.Anchor(
                                        SECTION_TITLES["app"],
                                        size="xl",
                                        href="/",
                                        underline=False,
                                    ),
                                    create_app_subtitle(),
                                ],
                            ),
                            span="content",
                        ),
                        dmc.GridCol(
                            dmc.Group(
                                justify="flex-end",
                                # TODO: Add GitHub link? Not sure if needed/wanted.
                            ),
                            span="auto",
                        ),
                    ],
                ),
            )
        ],
    )


def create_question_title():
    """Create the title for the map section of the dashboard."""
    return dmc.Stack(
        children=[
            dmc.Title(
                id="map-title",
                children=SECTION_TITLES["map_opinions"],
                order=3,
                fw=300,
            ),
            dmc.Text(
                id="map-subtitle",
                children=utils.create_question_subtitle(
                    question=DEFAULT_QUESTION["question"],
                    subquestion=DEFAULT_QUESTION["sub_question"],
                ),
                size="lg",
            ),
        ],
        gap="0",
    )


def create_impact_dropdown():
    """Create the dropdown for selecting the impact to display."""
    return dmc.Flex(
        dmc.Select(
            id="impact-select",
            label="View distribution of self-reported severe weather event",
            placeholder="Select a severe weather event",
            data=utils.get_impact_options(),
            clearable=True,
            searchable=True,
            nothingFoundMessage="No matches",
        ),
        justify="flex-end",
    )


def create_map_plot():
    """Create the component holding the cloropleth map plot of US states."""
    # TODO: Ensure that state click events are handled properly
    us_map = dmc.Container(
        # TODO: Make map margins smaller (or create a param for this, maybe), and make figure height larger (?)
        dcc.Graph(
            id="us-map",
            figure=make_map(
                question=DEFAULT_QUESTION["question"],
                sub_question=DEFAULT_QUESTION["sub_question"],
                outcome=DEFAULT_QUESTION["outcome"],
                # opinion_colormap=OPINION_COLORMAP,
            ),
            # vh = % of viewport height
            # TODO: Revisit once plot margins are adjusted
            style={"height": "65vh"},
        ),
        # sets max width
        # TODO: Revisit once plot margins are adjusted
        size="lg",
    )
    return us_map


def create_domain_heading(domain_text: str) -> dmc.Title:
    """Create a domain heading for the stacked bar plots."""
    return dmc.Title(
        id={
            "type": "domain-title",
            "domain": domain_text,
        },
        children=domain_text,
        order=4,
        fw=300,
        # Add some padding between the domain title and the question plots
        pb="md",
    )


def create_question_heading(question_label: str) -> dmc.Text:
    """Create a question heading for the stacked bar plots."""
    return dmc.Text(
        children=question_label,
        size="md",
    )


# TODO: Refactor args
def create_bar_plots_for_question(question_id: str, subquestion_id: str):
    """
    Create component to hold the stacked bar plot(s) for a single subquestion
    or all subquestions for a question.
    """
    figure = dmc.Container(
        dcc.Graph(
            id={
                "type": "stacked-bar-plot",
                "question": question_id,
            },
            figure=make_stacked_bar(
                question=question_id,
                subquestion=subquestion_id,
                state=None,
                stratify=False,
                threshold=DEFAULT_QUESTION["outcome"],
            ),
        ),
        w=1200,
        # size="xl",
    )
    return figure


def create_selected_question_bar_plot():
    """Create the component holding a title and stacked bar plot for the selected question."""
    title = dmc.Title(
        id="selected-question-title",
        children="Response distribution, National",
        order=4,
        fw=300,
    )

    figure = dmc.Container(
        dcc.Graph(
            id="selected-question-bar-plot",
            figure=make_stacked_bar(
                question=DEFAULT_QUESTION["question"],
                subquestion=DEFAULT_QUESTION["sub_question"],
                state=None,
                stratify=False,
                threshold=DEFAULT_QUESTION["outcome"],
                fig_kw=SINGLE_SUBQUESTION_FIG_KW,
            ),
        ),
        w=1200,
    )

    return dmc.Stack(
        id="selected-question-container",
        children=[
            title,
            figure,
        ],
        gap=0,
        align="center",
    )


def create_question_components(q_row: pd.Series) -> list:
    """Create a heading and stacked bar plot component for each question."""
    return [
        create_question_heading(q_row["full_text"]),
        create_bar_plots_for_question(q_row["question"], "all"),
    ]


def create_bar_plots_for_domain(domain_text: str):
    """Create component to hold the stacked bar plot(s) for all questions in a domain."""
    questions_df = DATA_DICTIONARIES["question_dictionary.tsv"]
    domain_df = questions_df.loc[
        questions_df["domain_text"] == domain_text
    ].copy()

    # Create a list that includes a heading and stacked bar plot for each question in the domain
    component_children = (
        domain_df.apply(create_question_components, axis=1).explode().tolist()
    )

    return dmc.Stack(
        component_children,
        gap="xs",
    )


def create_domain_tabs():
    """Create the tabs for each domain, each containing stacked bar plots for the questions in that domain."""
    tab_list = []
    panel_list = []

    for domain_short, domain_full in DOMAIN_TEXT.items():
        tab_list.append(
            dmc.TabsTab(
                domain_short,
                value=domain_full,
            )
        )
        panel_list.append(
            dmc.TabsPanel(
                id=domain_full,
                children=[
                    dcc.Loading(
                        id={
                            "type": "domain-loading-overlay",
                            "domain": domain_full,
                        },
                        children=[
                            create_domain_heading(domain_full),
                            create_bar_plots_for_domain(
                                domain_text=domain_full
                            ),
                        ],
                        overlay_style={
                            "visibility": "visible",
                            "filter": "blur(2px)",
                        },
                        type="circle",
                    ),
                ],
                value=domain_full,
                pt="sm",
            )
        )

    return dmc.Tabs(
        children=[dmc.TabsList(children=tab_list, grow=True)] + panel_list,
        orientation="horizontal",
        value=DOMAIN_TEXT[DEFAULT_QUESTION["domain"]],
    )


def create_main():
    """Create the main content of the dashboard."""
    return dmc.AppShellMain(
        children=[
            dmc.Container(
                my=25,
                mx="xs",
                fluid=True,
                children=[
                    create_question_title(),
                    create_impact_dropdown(),
                    create_map_plot(),
                    create_selected_question_bar_plot(),
                    create_domain_tabs(),
                ],
            )
        ]
    )


def construct_layout():
    """Generate the overall dashboard layout."""
    return dmc.AppShell(
        children=[create_header(), create_navbar(), create_main()],
        header={"height": HEADER_HEIGHT},
        navbar={"width": 400},
    )
