from dash import html, dcc


# ==================================================
# GLOBAL NAVIGATION
# ==================================================

GLOBAL_NAV = [
    ("Home", "/")
]


# ==================================================
# SKELETAL MUSCLE NAVIGATION
# ==================================================

MUSCLE_NAV = [
    ("Cohorts Overview", "/overview"),
    ("Gene (mRNA) Explorer", "/genes"),

    # Hidden for now
    # ("Differential Expression", "/differential-expression"),
    # ("Cross-cohort Validation", "/validation"),

    ("Pathway Enrichment", "/pathways"),
    ("Clinical Correlations", "/clinical"),
    ("miRNA Explorer", "/mirna"),
    ("mRNA Co-expression Networks", "/mrna-networks"),
    ("mRNA-miRNA Integration", "/integration"),
    ("Cellular Senescence", "/senescence"),
]


# ==================================================
# LINK STYLE
# ==================================================

LINK_STYLE = {
    "display": "block",
    "textDecoration": "none",
    "color": "var(--lab-navy-dark)",
    "fontSize": "14px",
    "fontWeight": "600",
    "padding": "9px 12px",
    "marginBottom": "2px",
    "borderRadius": "6px",
}


# ==================================================
# SIDEBAR
# ==================================================

def sidebar():

    return html.Div(
        [
            # ==========================================
            # SITE LABEL
            # ==========================================

            html.Div(
                "PAD Atlas",
                style={
                    "fontSize": "22px",
                    "fontWeight": "700",
                    "padding": "4px 8px 18px 8px",
                },
            ),


            # ==========================================
            # GLOBAL NAVIGATION
            # ==========================================

            html.Div(
                [
                    dcc.Link(
                        label,
                        href=href,
                        style=LINK_STYLE,
                    )
                    for label, href in GLOBAL_NAV
                ],

                style={
                    "paddingBottom": "15px",
                    "borderBottom": "1px solid #ddd",
                    "marginBottom": "15px",
                },
            ),


            # ==========================================
            # SKELETAL MUSCLE
            # ==========================================
            #
            # ONLY this section collapses.
            # ==========================================

            html.Details(
                [
                    html.Summary(
                        "Skeletal Muscle",

                        style={
                            "fontSize": "18px",
                            "fontWeight": "700",
                            "cursor": "pointer",
                            "padding": "9px 7px",
                            "userSelect": "none",
                        },
                    ),

                    html.Div(
                        [
                            dcc.Link(
                                label,
                                href=href,
                                style=LINK_STYLE,
                            )
                            for label, href in MUSCLE_NAV
                        ],

                        style={
                            "paddingTop": "5px",
                            "paddingLeft": "3px",
                        },
                    ),
                ],

                open=True,
            ),


            # ==================================================
            # MAINTAINED BY
            # ==================================================
            #
            # IMPORTANT:
            # This is OUTSIDE html.Details(),
            # so it never collapses with Skeletal Muscle.
            # ==================================================

            html.Div(
                [
                    html.Div(
                        "This website is maintained by:",

                        style={
                            "fontSize": "15px",
                            "fontWeight": "600",
                            "color": "var(--lab-muted)",
                            "marginBottom": "10px",
                            "textAlign": "center",
                        },
                    ),

                    html.A(
                        html.Div(
                            html.Img(
                                src=(
                                    "https://raw.githubusercontent.com/"
                                    "muharif/labwebsite/refs/heads/main/"
                                    "images/logo_withwebsite.svg"
                                ),

                                alt="Computational Multi-Omics Lab",

                                style={
                                    "width": "200px",
                                    "height": "auto",
                                    "display": "block",
                                },
                            ),

                            style={
                                "display": "flex",
                                "justifyContent": "center",
                                "alignItems": "center",
                                "width": "190px",
                            },
                        ),

                        href="https://multiomics.se/",
                        target="_blank",
                        title="Computational Multi-Omics Lab",

                        style={
                            "display": "flex",
                            "justifyContent": "center",
                            "textDecoration": "none",
                        },
                    ),
                ],

                style={
                    "marginTop": "28px",
                    "paddingTop": "20px",
                    "borderTop": "1px solid var(--lab-border)",
                    "paddingBottom": "15px",

                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "center",
                    "justifyContent": "center",

                    "width": "100%",
                    "boxSizing": "border-box",
                },
            ),


            # ==========================================
            # FUTURE BLOOD SECTION
            # ==========================================
            #
            # Hidden for now.
            #
            # Later:
            #
            # html.Details(
            #     [
            #         html.Summary("Blood"),
            #
            #         html.Div(
            #             [
            #                 ...
            #             ]
            #         ),
            #     ]
            # ),
        ],

        className="sidebar",
    )