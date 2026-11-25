import dash

from dash import (
    html,
    dcc,
    Input,
    Output,
    callback,
    dash_table,
)

from pad_atlas_public.utils.loaders import (
    load_table,
)

import plotly.express as px
from pad_atlas_public.utils.loaders import fold_change_plot, load_expression_summary, expression_summary_plot


dash.register_page(
    __name__,
    path="/genes",
    name="Gene (mRNA) Explorer",
)


GENE_CONTENT_WIDTH = "1340px"


comparison_labels = {
    "IC_VS_HC": "S-II vs HC",
    "CLI_VS_HC": "S-IV vs HC",
}


# ==================================================
# LOAD SMALL / MEDIUM TABLES
# ==================================================

features = load_table("features")
meta = load_table("mrna_meta")
de = load_table("mrna_deseq2")
modules = load_table("module_membership")
senescence = load_table("senescence_features")



# ==================================================
# mRNA GENE LIST
# ==================================================

genes = (
    features.loc[
        features["feature_type"] == "mrna",
        "feature_id",
    ]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .tolist()
)


default_gene = (
    "IGFBP6"
    if "IGFBP6" in genes
    else genes[0]
)


# ==================================================
# HELPERS
# ==================================================

def format_number(value, digits=3):

    if value is None:
        return "—"

    try:
        if value != value:
            return "—"
    except Exception:
        pass

    return f"{value:.{digits}f}"


def format_fdr(value):

    if value is None:
        return "—"

    try:
        if value != value:
            return "—"
    except Exception:
        pass

    if value < 0.001:
        return f"{value:.2e}"

    return f"{value:.4f}"


def metric_card(label, value):

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
                value,
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


def format_heterogeneity(i2):

    if i2 is None or i2 != i2:
        return "—"

    if i2 < 25:
        label = "Low"

    elif i2 < 50:
        label = "Moderate"

    elif i2 < 75:
        label = "Substantial"

    else:
        label = "High"

    return f"{i2:.1f}% · {label}"


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
            "Gene Explorer",
            style={
                "marginTop": 0,
            },
        ),

        html.P(
            "Explore cohort-specific and cross-cohort results "
            "for individual skeletal muscle genes."
        ),

        # --------------------------------------------------
        # Controls
        # --------------------------------------------------

        html.Div(
            [
                html.Div(
                    [
                        html.Label(
                            "Gene",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "13px",
                            },
                        ),

                        dcc.Dropdown(
                            id="gene-selector",
                            options=[
                                {
                                    "label": gene,
                                    "value": gene,
                                }
                                for gene in genes
                            ],
                            value=default_gene,
                            clearable=False,
                            searchable=True,
                        ),
                    ],
                    style={
                        "width": "320px",
                    },
                ),

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
                            id="gene-comparison-selector",
                
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
                "marginBottom": "30px",
            },
        ),

        # --------------------------------------------------
        # Dynamic output
        # --------------------------------------------------

        html.Div(
            id="gene-summary",
        ),
    ]
)


# ==================================================
# CALLBACK
# ==================================================

@callback(
    Output(
        "gene-summary",
        "children",
    ),
    Input(
        "gene-selector",
        "value",
    ),
    Input(
        "gene-comparison-selector",
        "value",
    ),
)
def update_gene_summary(
    gene,
    comparison,
):

    # ==================================================
    # META-ANALYSIS RESULT
    # ==================================================

    result = meta[
        (meta["feature_id"] == gene)
        &
        (meta["comparison_id"] == comparison)
    ]

    if result.empty:

        return html.Div(
            f"No meta-analysis result found for {gene}."
        )

    meta_row = result.iloc[0]


    # ==================================================
    # COHORT-SPECIFIC DESEQ2 RESULTS
    # ==================================================
    #
    # de_result:
    #     selected gene + selected comparison
    #     used for table and 2-cohort support
    #
    # gene_de:
    #     selected gene + BOTH comparisons
    #     used for persistent significance stars
    # ==================================================

    de_result = de[
        (de["feature_id"] == gene)
        &
        (de["comparison_id"] == comparison)
    ].copy()


    gene_de = de[
        de["feature_id"] == gene
    ].copy()


    cohort_order = [
        "DISCOVERY",
        "C2",
        "C3",
    ]


    cohort_labels = {
        "DISCOVERY": "Discovery",
        "C2": "Cohort 2",
        "C3": "Cohort 3",
    }


    # ==================================================
    # BUILD DESEQ2 TABLE
    # ==================================================

    de_rows = []


    for cohort_id in cohort_order:

        cohort_de = de_result[
            de_result["cohort_id"] == cohort_id
        ]

        if cohort_de.empty:

            de_rows.append(
                {
                    "cohort": cohort_labels[cohort_id],

                    "log2_fold_change": "—",
                    "lfc_se": "—",
                    "stat": "—",
                    "p_value": "—",
                    "fdr": "—",
                    "significant": "",
                }
            )

            continue


        de_row = cohort_de.iloc[0]


        de_rows.append(
            {
                "cohort": cohort_labels[cohort_id],

                "log2_fold_change": format_number(
                    de_row["log2_fold_change"],
                    3,
                ),

                "lfc_se": format_number(
                    de_row["lfc_se"],
                    3,
                ),

                "stat": format_number(
                    de_row["stat"],
                    3,
                ),

                "p_value": format_fdr(
                    de_row["p_value"]
                ),

                "fdr": format_fdr(
                    de_row["fdr"]
                ),

                "significant": significance_stars(
                    de_row["fdr"]
                ),
            }
        )


    # ==================================================
    # EXPRESSION
    # ==================================================

    box_fig = expression_summary_plot(load_expression_summary("mrna", gene), gene_de, cohort_labels, significance_stars, "log2(TPM + 1)")
    expression_fig = fold_change_plot(gene_de, cohort_labels, significance_stars, show_se=True)

    # ==================================================
    # MODULE MEMBERSHIP
    # ==================================================

    module_result = modules[
        (modules["feature_id"] == gene)
        &
        (modules["feature_type"] == "mrna")
    ]


    if module_result.empty:

        module_id = "—"
        degree = "—"

    else:

        module_row = module_result.iloc[0]

        module_id = module_row["module_id"]

        degree = format_number(
            module_row["degree"],
            0,
        )


    # ==================================================
    # SENESCENCE MEMBERSHIP
    # ==================================================

    sen_result = senescence[
        senescence["feature_id"] == gene
    ]


    if sen_result.empty:

        senescence_sources = (
            "Not in curated sets"
        )

    else:

        senescence_sources = (
            sen_result.iloc[0][
                "senescence_sources"
            ]
        )


    # ==================================================
    # CROSS-COHORT SUPPORT
    # ==================================================
    #
    # Strict manuscript consensus:
    #     consensus_fe == True
    #
    # Relaxed visual support:
    #     at least two cohort-specific significant
    #     DESeq2 results with the same direction
    # ==================================================

    sig_de = de_result[
        de_result["fdr"].notna()
        &
        (de_result["fdr"] < 0.05)
        &
        de_result[
            "log2_fold_change"
        ].notna()
    ].copy()


    sig_de["de_direction"] = (
        sig_de["log2_fold_change"]
        .apply(
            lambda x:
                "Up"
                if x > 0

                else "Down"
                if x < 0

                else "Neutral"
        )
    )


    direction_counts = (
        sig_de["de_direction"]
        .value_counts()
    )


    two_cohort_consensus = (
        not direction_counts.empty
        and direction_counts.max() >= 2
    )


    if bool(meta_row["consensus_fe"]):

        consensus = "Yes (3)"

    elif two_cohort_consensus:

        consensus = "Yes (2)"

    else:

        consensus = "No"


    # ==================================================
    # META-ANALYSIS DIRECTION
    # ==================================================

    meta_lfc = meta_row["meta_lfc_fe"]
    meta_fdr = meta_row["meta_fdr_fe"]


    if (
        meta_lfc is None
        or meta_lfc != meta_lfc
        or meta_fdr is None
        or meta_fdr != meta_fdr
    ):

        meta_direction = "—"


    elif meta_fdr >= 0.05:

        meta_direction = "NS"


    elif meta_lfc > 0:

        meta_direction = "Up-Regulated"


    elif meta_lfc < 0:

        meta_direction = "Down-Regulated"


    else:

        meta_direction = "NS"


    # ==================================================
    # PAGE OUTPUT
    # ==================================================

    return html.Div(
        [
            # ==================================================
            # GENE TITLE + EXTERNAL LINKS
            # ==================================================

            html.Div(
                [
                    html.H2(
                        gene,
                        style={
                            "margin": 0,
                        },
                    ),

                    html.A(
                        "GeneCards ↗",
                        href=(
                            "https://www.genecards.org/"
                            f"cgi-bin/carddisp.pl?gene={gene}"
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
                    ),

                    html.A(
                        "Human Protein Atlas ↗",
                        href=(
                            "https://www.proteinatlas.org/"
                            f"search/{gene}"
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
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "marginBottom": "6px",
                    "flexWrap": "wrap",
                },
            ),


            # ==================================================
            # SENESCENCE MEMBERSHIP
            # ==================================================

            html.Div(
                f"Senescence sets: {senescence_sources}",
                style={
                    "marginBottom": "20px",
                },
            ),


            # ==================================================
            # META CARDS
            # ==================================================

            html.Div(
                [
                    metric_card(
                        "Meta LFC",
                        format_number(
                            meta_row["meta_lfc_fe"]
                        ),
                    ),

                    metric_card(
                        "Meta FDR",
                        format_fdr(
                            meta_row["meta_fdr_fe"]
                        ),
                    ),

                    metric_card(
                        "Cross-cohort consensus",
                        consensus,
                    ),

                    metric_card(
                        "Meta direction",
                        meta_direction,
                    ),

                    metric_card(
                        "Cross-cohort variability (I²)",
                        format_heterogeneity(
                            meta_row["i2"]
                        ),
                    ),

                    metric_card(
                        "mRNA module",
                        str(module_id),
                    ),

                    metric_card(
                        "Degree Centrality",
                        str(degree),
                    ),
                ],
                style={
                    "display": "flex",
                    "gap": "12px",
                    "flexWrap": "wrap",
                    "marginBottom": "30px",
                },
            ),


            # ==================================================
            # EXPRESSION + DESEQ2 TABLE WRAPPER
            # ==================================================

            html.Div(
                [
                    # ------------------------------------------
                    # EXPRESSION
                    # ------------------------------------------

                    html.Div(
                        [
                            html.H3(
                                "Expression and differential expression across cohorts",
                                style={
                                    "marginTop": 0,
                                    "marginBottom": "4px",
                                    "width": "100%",
                                    "boxSizing": "border-box",
                                },
                            ),

                            html.P(
                                
                                "Asterisks indicate cohort-specific DESeq2 "
                                "significance versus HC for both S-II and S-IV ",

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
                                        dcc.Graph(figure=expression_fig, config={"displaylogo": False}),
                                        html.P("Log2 fold change versus HC. Error bars show LFC standard errors.", className="atlas-plot-caption"),
                                    ]),
                                ],
                            ),
                        ],

                        style={
                            "border": "1px solid #ddd",
                            "borderRadius": "8px",
                            "padding": "20px",
                            "marginBottom": "20px",
                            "width": "100%",
                            "boxSizing": "border-box",
                        },
                    ),


                    # ------------------------------------------
                    # COHORT-SPECIFIC DESEQ2 RESULTS
                    # ------------------------------------------

                    html.Div(
                        [
                            html.H3(
                                "Cohort-specific differential expression",

                                style={
                                    "marginTop": 0,
                                    "marginBottom": "5px",
                                },
                            ),

                            html.P(
                                [
                                    "DESeq2 results for the selected "
                                    "comparison in each cohort: ",

                                    html.Strong(
                                        comparison_labels.get(
                                            comparison,
                                            comparison,
                                        )
                                    ),
                                ],

                                style={
                                    "marginTop": "0",
                                    "marginBottom": "12px",
                                },
                            ),

                            dash_table.DataTable(
                                columns=[
                                    {
                                        "name": "Cohort",
                                        "id": "cohort",
                                    },
                                    {
                                        "name": "log2 fold change",
                                        "id": "log2_fold_change",
                                    },
                                    {
                                        "name": "LFC SE",
                                        "id": "lfc_se",
                                    },
                                    {
                                        "name": "Wald statistic",
                                        "id": "stat",
                                    },
                                    {
                                        "name": "P value",
                                        "id": "p_value",
                                    },
                                    {
                                        "name": "FDR",
                                        "id": "fdr",
                                    },
                                    {
                                        "name": "Significance",
                                        "id": "significant",
                                    },
                                ],

                                data=de_rows,

                                page_action="none",

                                style_table={
                                    "overflowX": "auto",
                                    "width": "100%",
                                },

                                style_header={
                                    "fontWeight": "bold",
                                    "backgroundColor": "#f7f7f7",
                                    "borderBottom": "2px solid #ddd",
                                    "textAlign": "left",
                                    "padding": "10px",
                                },

                                style_cell={
                                    "fontFamily": "Arial, sans-serif",
                                    "fontSize": "14px",
                                    "padding": "10px",
                                    "textAlign": "left",
                                    "border": "none",
                                    "borderBottom": "1px solid #eee",
                                    "minWidth": "90px",
                                    "maxWidth": "160px",
                                },

                                style_cell_conditional=[
                                    {
                                        "if": {
                                            "column_id": "cohort",
                                        },

                                        "fontWeight": "600",
                                        "minWidth": "110px",
                                    },
                                ],

                                style_data_conditional=[
                                    {
                                        "if": {
                                            "filter_query":
                                                "{significant} != ''",
                                        },

                                        "fontWeight": "600",
                                    },
                                ],
                            ),
                        ],

                        style={
                            "border": "1px solid #ddd",
                            "borderRadius": "8px",
                            "padding": "20px",
                            "width": "100%",
                            "boxSizing": "border-box",
                        },
                    ),
                ],

                style={
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "width": "100%",
                    "maxWidth": GENE_CONTENT_WIDTH,
                    "boxSizing": "border-box",
                },
            ),
        ]
    )