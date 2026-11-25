import dash

from dash import (
    html,
    dcc,
    Input,
    Output,
    callback,
)

import plotly.express as px
from pad_atlas_public.utils.loaders import fold_change_plot, load_expression_summary, expression_summary_plot

from pad_atlas_public.utils.loaders import load_table


dash.register_page(
    __name__,
    path="/mirna",
    name="miRNA Explorer",
)


# ==================================================
# LOAD TABLES
# ==================================================

mirna_de = load_table(
    "mirna_de"
)


membership = load_table(
    "module_membership"
)




# ==================================================
# miRNA MODULES
# ==================================================

mirna_modules = membership[
    membership["feature_type"] == "mirna"
].copy()


# ==================================================
# miRNA LIST
# ==================================================

MIRNAS = sorted(
    mirna_de["feature_id"]
    .dropna()
    .unique()
)


default_mirna = (
    "hsa-miR-2392"
    if "hsa-miR-2392" in MIRNAS
    else MIRNAS[0]
)


# ==================================================
# GENECARDS MAPPING
# ==================================================

MIRNA_GENECARDS = dict(zip(MIRNAS,[(i.split("-")[1]+i.split("-")[2]).upper() for i in MIRNAS]))


# ==================================================
# HELPERS
# ==================================================

def card(value, label):

    return html.Div(
        [
            html.Div(
                label,
                style={
                    "fontSize": "12px",
                    "fontWeight": "bold",
                    "marginBottom": "7px",
                },
            ),

            html.Div(
                str(value),
                style={
                    "fontSize": "22px",
                    "fontWeight": "600",
                },
            ),
        ],
        style={
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "padding": "16px",
            "minWidth": "150px",
        },
    )


def format_number(
    value,
    digits=3,
):

    if value is None or value != value:
        return "—"

    return f"{value:.{digits}f}"


def format_fdr(value):

    if value is None or value != value:
        return "—"

    if value < 0.001:
        return f"{value:.2e}"

    return f"{value:.4f}"


def significance_stars(fdr):

    if fdr is None or fdr != fdr:
        return ""

    if fdr < 0.0001:
        return "****"

    if fdr < 0.001:
        return "***"

    if fdr < 0.01:
        return "**"

    if fdr < 0.05:
        return "*"

    return ""


# ==================================================
# PAGE
# ==================================================

layout = html.Div(
    [
        html.H1(
            "miRNA Explorer",
            style={
                "marginTop": 0,
            },
        ),

        html.P(
            "Explore Discovery-cohort skeletal muscle miRNA "
            "expression and differential expression."
        ),

        # --------------------------------------------------
        # Controls
        # --------------------------------------------------

        html.Div(
            [
                # miRNA selector
                html.Div(
                    [
                        html.Label(
                            "miRNA",
                            style={
                                "fontWeight": "bold",
                            },
                        ),

                        dcc.Dropdown(
                            id="mirna-selector",

                            options=[
                                {
                                    "label": mir,
                                    "value": mir,
                                }
                                for mir in MIRNAS
                            ],

                            value=default_mirna,

                            searchable=True,
                            clearable=False,
                        ),
                    ],
                    style={
                        "width": "330px",
                    },
                ),

                # Comparison selector
                html.Div(
                    [
                        html.Label(
                            "Comparison",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "13px",
                                "display": "block",
                                "marginBottom": "8px",
                            },
                        ),

                        dcc.RadioItems(
                            id="mirna-comparison",

                            options=[
                                {
                                    "label": "S-II vs HC",
                                    "value": "IC_VS_HC",
                                },
                                {
                                    "label": "S-IV vs HC",
                                    "value": "CLI_VS_HC",
                                },
                            ],

                            value="CLI_VS_HC",

                            inline=True,

                            labelStyle={
                                "display": "inline-flex",
                                "alignItems": "center",
                                "marginRight": "22px",
                                "fontSize": "18px",
                                "fontWeight": "600",
                                "cursor": "pointer",
                            },

                            inputStyle={
                                "marginRight": "7px",
                                "cursor": "pointer",
                            },
                        ),
                    ],
                    style={
                        "minWidth": "300px",
                    },
                ),
            ],

            style={
                "display": "flex",
                "gap": "20px",
                "flexWrap": "wrap",
                "marginBottom": "28px",
            },
        ),

        html.Div(
            id="mirna-content",
        ),
    ]
)


# ==================================================
# CALLBACK
# ==================================================

@callback(
    Output(
        "mirna-content",
        "children",
    ),

    Input(
        "mirna-selector",
        "value",
    ),

    Input(
        "mirna-comparison",
        "value",
    ),
)
def update_mirna(
    feature_id,
    comparison_id,
):

    # ==================================================
    # SELECTED COMPARISON
    # ==================================================

    selected_de = mirna_de[
        (mirna_de["feature_id"] == feature_id)
        &
        (
            mirna_de["comparison_id"]
            == comparison_id
        )
    ].copy()


    if selected_de.empty:

        lfc = None
        fdr = None
        direction = "—"

    else:

        de_row = selected_de.iloc[0]

        lfc = de_row[
            "log2_fold_change"
        ]

        fdr = de_row[
            "fdr"
        ]


        if (
            fdr != fdr
            or fdr >= 0.05
        ):

            direction = "NS"


        elif lfc > 0:

            direction = "Up"


        elif lfc < 0:

            direction = "Down"


        else:

            direction = "NS"


    # ==================================================
    # BOTH COMPARISONS
    #
    # Used for persistent significance stars.
    # These do not depend on the radio button.
    # ==================================================

    gene_de = mirna_de[
        mirna_de["feature_id"]
        == feature_id
    ].copy()


    # miRNA dataset is Discovery-only, but be explicit
    if "cohort_id" in gene_de.columns:

        gene_de = gene_de[
            gene_de["cohort_id"]
            == "DISCOVERY"
        ].copy()


    # ==================================================
    # MODULE MEMBERSHIP
    # ==================================================

    module = mirna_modules[
        mirna_modules["feature_id"]
        == feature_id
    ]


    if module.empty:

        module_id = "—"
        degree = "—"

    else:

        module_row = module.iloc[0]

        module_id = module_row[
            "module_id"
        ]

        degree = format_number(
            module_row["degree"],
            0,
        )


    # ==================================================
    # EXPRESSION
    # ==================================================

    box_fig = expression_summary_plot(load_expression_summary("mirna", feature_id), gene_de, {"DISCOVERY": "Discovery"}, significance_stars, "log TPM")
    fig = fold_change_plot(gene_de, {"DISCOVERY": "Discovery"}, significance_stars)

    # ==================================================
    # GENECARDS LINK
    # ==================================================

    genecards_symbol = (
        MIRNA_GENECARDS.get(
            feature_id
        )
    )


    # ==================================================
    # RETURN PAGE CONTENT
    # ==================================================

    return html.Div(
        [
            # --------------------------------------------------
            # miRNA name + GeneCards
            # --------------------------------------------------

            html.Div(
                [
                    html.H2(
                        feature_id,
                        style={
                            "margin": 0,
                        },
                    ),

                    (
                        html.A(
                            "GeneCards ↗",

                            href=(
                                "https://www.genecards.org/card/"
                                f"{genecards_symbol}"
                            ),

                            target="_blank",
                            rel="noopener noreferrer",

                            style={
                                "fontSize": "13px",
                                "fontWeight": "600",
                                "textDecoration": "none",
                                "color": "var(--lab-blue)",
                                "marginLeft": "12px",
                            },
                        )

                        if genecards_symbol
                        else None
                    ),
                ],

                style={
                    "display": "flex",
                    "alignItems": "center",
                    "flexWrap": "wrap",
                    "marginBottom": "18px",
                },
            ),


            # --------------------------------------------------
            # Summary cards
            # --------------------------------------------------

            html.Div(
                [
                    card(
                        format_number(lfc),
                        "log2 fold change",
                    ),

                    card(
                        format_fdr(fdr),
                        "FDR",
                    ),

                    card(
                        direction,
                        "Direction",
                    ),

                    card(
                        module_id,
                        "miRNA module",
                    ),

                    card(
                        degree,
                        "Degree centrality",
                    ),
                ],

                style={
                    "display": "flex",
                    "gap": "12px",
                    "flexWrap": "wrap",
                    "marginBottom": "24px",
                },
            ),


            # --------------------------------------------------
            # Expression
            # --------------------------------------------------

            html.Div(
                [
                    html.H3(
                        "Discovery expression and differential expression",
                        style={
                            "marginTop": 0,
                            "marginBottom": "4px",
                        },
                    ),

                    html.P(
                        "Asterisks indicate Discovery-cohort "
                        "differential expression versus HC "
                        "for both disease stages ",

                        style={
                            "marginTop": 0,
                            "marginBottom": "10px",
                        },
                    ),
                    html.P(

                        "(* FDR < 0.05, ** < 0.01, "
                        "*** < 0.001, **** < 0.0001).",

                        style={
                            "marginTop": 0,
                            "marginBottom": "10px",
                        },
                    ),
                    dcc.Tabs(
                        className="atlas-plot-selector",
                        parent_className="atlas-plot-selector-parent",
                        value="expression",
                        children=[
                            dcc.Tab(className="atlas-plot-option", selected_className="atlas-plot-option-active", label="Expression", value="expression", children=[
                                dcc.Graph(figure=box_fig, config={"displaylogo": False}),
                                html.P("Group summaries only; no individual sample points.", className="atlas-plot-caption"),
                            ]),
                            dcc.Tab(className="atlas-plot-option", selected_className="atlas-plot-option-active", label="Log2 Fold Change", value="fold_change", children=[
                                dcc.Graph(figure=fig, config={"displaylogo": False}),
                                html.P("Log2 fold change versus HC.", className="atlas-plot-caption"),
                            ]),
                        ],
                    ),
                ],

                style={
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "maxWidth": "850px",
                },
            ),
        ]
    )