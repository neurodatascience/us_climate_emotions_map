"""Generate the layout for the dashboard."""

import dash_mantine_components as dmc
import pandas as pd
from dash import dcc, html

from . import utility as utils
from .data_loader import DATA_DICTIONARIES, DOMAIN_TEXT, PRERENDERED_BARPLOTS
from .make_descriptive_plots import make_descriptive_plots
from .make_map import make_map
from .make_stacked_bar_plots import make_stacked_bar
from .utility import (  # IMPACT_COLORMAP,; OPINION_COLORMAP,
    ALL_STATES_LABEL,
    DEFAULT_QUESTION,
    NUM_DECIMALS,
    SECTION_TITLES,
)

HEADER_HEIGHT = 110

SUPP_TEXT = {
    "paper_link": "https://www.thelancet.com/journals/lanplh/article/PIIS2542-5196(24)00229-8/fulltext",
    "more_info_link": "https://docs.google.com/document/d/e/2PACX-1vQVssAsC0ddI41vlVYZnS_hxOj6UTbvWVeiejjHRSAzgDzPMFZaM25dWxbdyDOFBJi0KlTlnUUSqjWU/pub",
    "hover_tip": "Hover over bars for full proportions",
    "weighted_descriptives": "*N are unweighted while proportions are weighted according to US census estimates for age, sex, race, and ethnicity",
    "map_disclaimer": "Map does not support making statistical comparisons between states",
}

MAP_LAYOUT = {
    "margin": {"l": 15, "r": 15, "t": 15, "b": 15},
    "colormap_range_padding": 0,
}

SINGLE_SUBQUESTION_FIG_KW = {
    "fontsize": 10,
    "height": 120,
    "margin": {"l": 30, "r": 30, "t": 10, "b": 20},
}

# See https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js for all options
DCC_GRAPH_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
    "doubleClick": "reset",
}


def create_mobile_warning():
    """Create an alert to be displayed on mobile devices or small screens."""
    return dmc.Alert(
        children=[
            "Graphics on this site are not optimized for mobile devices or small screens. ",
            "For the best experience, please view it full-screen on a laptop or desktop.",
        ],
        title="Larger screen size recommended",
        color="yellow",
        hiddenFrom="sm",
        mb="sm",
    )


def create_question_dropdown():
    """
    Create the dropdown for subquestions grouped by question.
    NOTE: 'value' must be a string for DMC, so we use f-strings to concatenate the question and subquestion.
    NOTE: Some questions include a '_' character in the id, so when extracting the question and subquestion we always need to split on the last '_'.
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
            "group": {
                "paddingTop": 4,
                "paddingBottom": 4,
                "borderBottom": "1px solid #E6E6E6",
            },
            "groupLabel": {"color": "#228BE6"},
            "option": {"paddingTop": 4, "paddingBottom": 4},
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


def create_sample_descriptives_hover_tip():
    """Create the tip to hover over bars in the sample characteristics drawer."""
    return dmc.Text(
        children=SUPP_TEXT["hover_tip"],
        fs="italic",
        size="sm",
        mt="xs",
    )


def create_sample_descriptive_note():
    """Create the note for the sample characteristics section."""
    return dmc.Text(
        children=SUPP_TEXT["weighted_descriptives"],
        size="xs",
    )


def create_sample_descriptive_plot():
    """Create the component holding the subplots of sample descriptive statistics."""
    return dcc.Graph(
        id="sample-descriptive-plot",
        figure=make_descriptive_plots(
            state=None,
            decimals=NUM_DECIMALS,
        ),
        config=DCC_GRAPH_CONFIG,
        # TODO: Revisit
        # We use px instead of viewport height here for now to more easily control scrolling
        # on smaller screens
        style={"height": "1000px"},
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
                    create_sample_descriptives_hover_tip(),
                    create_sample_descriptive_plot(),
                    create_sample_descriptive_note(),
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
                size="40%",
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
        children="Web application built by members of the ORIGAMI Lab",
        ta="center",
        size="xs",
        c="dimmed",
    )

    long_credit = dmc.Text(
        children=[
            "Developers from the ",
            dmc.Anchor(
                "ORIGAMI Neuro Data Science Lab (PI: Jean-Baptiste Poline)",
                href="https://neurodatascience.github.io/",
                target="_blank",
                style={"display": "inline"},
            ),
            " - Alyssa Dai, Michelle Wang, Nikhil Bhagwat, Arman Jahanpour, Kendra Oudyk, Rémi Gau, Sebastian Urchs - ",
            "created this web app which is provided as is with no guarantee, ",
            "but were not involved in the design, analysis, and reporting of the project. ",
            "The project results and interpretation are entirely the responsibility of the article authors.",
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
            "Graphical appendix for ",
            dmc.Anchor(
                children=[
                    '"Climate emotions, thoughts, and plans among US adolescents and young adults: a cross-sectional descriptive survey and analysis by political party identification and self-reported exposure to severe weather events." ',
                    "[Lewandowski, R.E, Clayton, S.D., Olbrich, L., Sakshaug, J.W., Wray, B. et al, (2024) ",
                    html.I(
                        "The Lancet Planetary Health, ",
                    ),
                    "11 (8)]",
                ],
                href=SUPP_TEXT["paper_link"],
                target="_blank",
                style={"display": "inline"},
                # Inherit font properties from parent
                inherit=True,
            ),
        ],
        style={"display": "inline"},
        size="sm",
        fw=500,
        visibleFrom="sm",
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
                                    dmc.Grid(
                                        children=[
                                            dmc.GridCol(
                                                dmc.Anchor(
                                                    SECTION_TITLES["app"],
                                                    size="xl",
                                                    href="/",
                                                    underline=False,
                                                ),
                                                span="content",
                                            ),
                                            dmc.GridCol(
                                                dmc.Anchor(
                                                    SECTION_TITLES[
                                                        "more_info"
                                                    ],
                                                    href=SUPP_TEXT[
                                                        "more_info_link"
                                                    ],
                                                    target="_blank",
                                                ),
                                                span="content",
                                            ),
                                        ],
                                        justify="space-between",
                                        align="flex-end",
                                    ),
                                    create_app_subtitle(),
                                ],
                            ),
                            span="12",
                        ),
                    ],
                ),
            )
        ],
    )


def create_map_title():
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
    return dmc.Select(
        id="impact-select",
        label="Distribution of severe weather events (self-reported)",
        placeholder="Select a severe weather event",
        data=utils.get_impact_options(),
        clearable=True,
        searchable=True,
        nothingFoundMessage="No matches",
    )


def create_map_plot():
    """Create the component holding the cloropleth map plot of US states."""
    us_map = dmc.Container(
        dcc.Graph(
            id="us-map",
            figure=make_map(
                question=DEFAULT_QUESTION["question"],
                sub_question=DEFAULT_QUESTION["sub_question"],
                outcome=DEFAULT_QUESTION["outcome"],
                colormap_range_padding=MAP_LAYOUT["colormap_range_padding"],
                margins=MAP_LAYOUT["margin"],
                decimals=NUM_DECIMALS,
                # opinion_colormap=OPINION_COLORMAP,
            ),
            # vh = % of viewport height
            # TODO: Revisit once plot margins are adjusted
            config=DCC_GRAPH_CONFIG,
            style={"height": "65vh"},
        ),
        # set max width
        # TODO: Revisit once plot margins are adjusted
        # style={"maxWidth": "70vw"},
        size="xl",
    )
    return us_map


def create_map_disclaimer():
    """Create the disclaimer for the map section of the dashboard."""
    return dmc.Flex(
        [
            html.I(
                className="bi bi-exclamation-circle", style={"fontSize": 15}
            ),
            dmc.Text(
                children=SUPP_TEXT["map_disclaimer"],
                fs="italic",
                size="sm",
                # ta="center",
            ),
        ],
        gap=5,
        align="center",
    )


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
            figure=PRERENDERED_BARPLOTS[
                None, False, DEFAULT_QUESTION["outcome"], NUM_DECIMALS
            ][question_id],
            config=DCC_GRAPH_CONFIG,
        ),
        fluid=True,
        # TODO: Reduce currently hard-coded L/R margins in Plotly fig to fill up more available width
        w={"base": "100vw", "lg": 1000},
        # size="xl",
    )
    return figure


def create_selected_question_bar_plot():
    """Create the component holding a title and stacked bar plot for the selected question."""
    title = dmc.Title(
        id="selected-question-title",
        children=ALL_STATES_LABEL,
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
                decimals=NUM_DECIMALS,
                fig_kw=SINGLE_SUBQUESTION_FIG_KW,
            ),
            config=DCC_GRAPH_CONFIG,
        ),
        fluid=True,
        # TODO: Reduce currently hard-coded L/R margins in Plotly fig to fill up more available width
        w={"base": "100vw", "lg": 1000},
    )

    return dmc.Stack(
        id="selected-question-container",
        children=[
            title,
            figure,
        ],
        gap=0,
        align="center",
        pb="sm",
    )


def create_all_questions_section_title() -> dmc.Title:
    """Create a title for the section containing the bar plots for all questions."""
    return dmc.Title(
        id="all-questions-title",
        children=f"{SECTION_TITLES['all_questions']}: {ALL_STATES_LABEL}",
        order=3,
        fw=300,
        pb="sm",
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
                    create_mobile_warning(),
                    create_map_title(),
                    dmc.Grid(
                        [
                            dmc.GridCol(
                                create_map_disclaimer(),
                                span="content",
                            ),
                            dmc.GridCol(
                                create_impact_dropdown(),
                                span="content",
                            ),
                        ],
                        justify="space-between",
                        align="flex-end",
                    ),
                    create_map_plot(),
                    create_selected_question_bar_plot(),
                    create_all_questions_section_title(),
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
        navbar={
            "width": 300,
            "breakpoint": "sm",
            "collapsed": {"mobile": True},
        },
    )
