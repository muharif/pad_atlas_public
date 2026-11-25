import dash

from dash import (
    html,
    dcc,
)


dash.register_page(
    __name__,
    path="/",
    name="Home",
)


# ============================================================
# COLORS / COMMON STYLES
# ============================================================

SECTION_STYLE = {
    "maxWidth": "1050px",
    "marginBottom": "34px",
}


CARD_STYLE = {
    "border": "1px solid var(--lab-border)",
    "borderRadius": "8px",
    "padding": "18px",
    "backgroundColor": "transparent",
    "boxSizing": "border-box",
}


TOOL_LINK_STYLE = {
    "textDecoration": "none",
    "color": "inherit",
}


# ============================================================
# TOOL CARD
# ============================================================

def tool_card(
    title,
    description,
    href,
):

    return dcc.Link(
        html.Div(
            [
                html.Div(
                    title,

                    style={
                        "fontSize": "17px",
                        "fontWeight": "700",
                        "color": "var(--lab-navy-dark)",
                        "marginBottom": "6px",
                    },
                ),

                html.Div(
                    description,

                    style={
                        "fontSize": "13px",
                        "lineHeight": "1.45",
                        "color": "var(--lab-muted)",
                    },
                ),
            ],

            style={
                **CARD_STYLE,

                "height": "100%",
                "transition":
                    "transform 0.15s ease, "
                    "box-shadow 0.15s ease",
            },
        ),

        href=href,
        style=TOOL_LINK_STYLE,
    )


# ============================================================
# PAGE
# ============================================================

layout = html.Div(
    [
        # ====================================================
        # ABOUT
        # ====================================================

        html.Section(
            [
                html.H2(
                    "About",

                    style={
                        "marginTop": 0,
                        "marginBottom": "12px",
                    },
                ),

                html.P(
                    [
                        "PAD Atlas is an interactive platform for "
                        "exploring and visualizing multi-omics data "
                        "from skeletal muscle in peripheral artery "
                        "disease. The resource was developed by the ",

                        html.A(
                            "Computational Multi-Omics Lab",

                            href="https://multiomics.se/",
                            target="_blank",

                            style={
                                "color": "var(--lab-blue)",
                                "fontWeight": "600",
                            },
                        ),

                        " at the University of Gothenburg together with our collaborators in the ",
                        html.A(
                            "University of Nebraska Medical Center",

                            href="https://www.unmc.edu/physiology/faculty/koutakis.html",
                            target="_blank",

                            style={
                                "color": "var(--lab-blue)",
                                "fontWeight": "600",
                            },
                        ),
                        " to support research data sharing, "
                        "reproducibility, and openness in science.",
                    ],

                    style={
                        "lineHeight": "1.65",
                        "marginBottom": "14px",
                    },
                ),

                html.P(
                    (
                        "The platform is designed to make the study "
                        "results accessible to a broad audience, "
                        "including clinicians, experimental scientists, "
                        "and researchers without specialized "
                        "bioinformatics or systems-biology training."
                    ),

                    style={
                        "lineHeight": "1.65",
                        "marginBottom": "14px",
                    },
                ),

                html.P(
                    (
                        "PAD Atlas currently focuses on skeletal-muscle "
                        "mRNA and miRNA data together with pathway, "
                        "network, clinical-correlation, and cellular "
                        "senescence analyses. The platform can be "
                        "expanded as additional omics datasets and "
                        "analyses become available."
                    ),

                    style={
                        "lineHeight": "1.65",
                        "marginBottom": 0,
                    },
                ),
            ],

            style=SECTION_STYLE,
        ),


        # ====================================================
        # FEATURES / GENERAL EXPLANATION
        # ====================================================

        html.Section(
            [
                html.H2(
                    "Features",

                    style={
                        "marginTop": 0,
                        "marginBottom": "12px",
                    },
                ),

                html.P(
                    (
                        "The atlas provides interactive views of "
                        "precomputed statistical results generated "
                        "during the study analyses. Users can inspect "
                        "individual genes and miRNAs, compare disease "
                        "stages and cohorts, examine enriched pathways, "
                        "and explore co-expression and integrated "
                        "multi-omic networks."
                    ),

                    style={
                        "lineHeight": "1.65",
                        "marginBottom": "14px",
                    },
                ),

                html.P(
                    (
                        "Where appropriate, external resources such as "
                        "GeneCards and the Human Protein Atlas, are linked directly from "
                        "the relevant explorer pages."
                    ),

                    style={
                        "lineHeight": "1.65",
                        "marginBottom": 0,
                    },
                ),
            ],

            style=SECTION_STYLE,
        ),


        # ====================================================
        # CITATION
        # ====================================================

        html.Section(
            [
                html.H2(
                    "Citation",

                    style={
                        "marginTop": 0,
                        "marginBottom": "12px",
                    },
                ),

                html.P(
                    (
                        "If you use PAD Atlas, please cite the primary "
                        "study associated with these data."
                    ),

                    style={
                        "lineHeight": "1.65",
                        "marginBottom": "12px",
                    },
                ),

                # ------------------------------------------------
                # PLACEHOLDER — replace when manuscript is ready
                # ------------------------------------------------

                html.Div(
                    [
                        html.Strong(
                            "Suggested citation"
                        ),

                        html.Div(
                            (
                                "Coming Soon!"
                            ),

                            style={
                                "marginTop": "7px",
                                "lineHeight": "1.55",
                            },
                        ),
                    ],

                    style={
                        **CARD_STYLE,
                        "maxWidth": "850px",
                    },
                ),

            ],

            style=SECTION_STYLE,
        ),


        # ====================================================
        # CONTACT
        # ====================================================

        html.Section(
            [
                html.H2(
                    "Contact",

                    style={
                        "marginTop": 0,
                        "marginBottom": "12px",
                    },
                ),

                html.P(
                    [
                        "For questions, suggestions, or issues related "
                        "to PAD Atlas, please contact the PI of ",

                        html.A(
                            "Computational Multi-Omics Lab",

                            href="https://multiomics.se/#team",
                            target="_blank",

                            style={
                                "color": "var(--lab-blue)",
                                "fontWeight": "600",
                            },
                        ),

                        ", Muhammad Arif.",
                    ],

                    style={
                        "lineHeight": "1.65",
                        "marginBottom": "9px",
                    },
                ),

            ],

            style={
                **SECTION_STYLE,
                "paddingBottom": "30px",
            },
        ),
    ],

    style={
        "maxWidth": "1100px",
    },
)