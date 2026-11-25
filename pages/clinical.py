import dash

from dash import (
    html,
    dcc,
    Input,
    Output,
    callback,
    dash_table,
)

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from pad_atlas_public.utils.loaders import load_table


dash.register_page(
    __name__,
    path="/clinical",
    name="Clinical Correlations",
)


# ==================================================
# LOAD DATA
# ==================================================

clinical = load_table(
    "clinical_correlations"
)


# ==================================================
# LABELS
# ==================================================

COHORT_LABELS = {
    "DISCOVERY": "Discovery",
    "C2": "Cohort 2",
    "C3": "Cohort 3",
}


CLINICAL_LABELS = {
    "abi": "ABI",
    "six_min_walk_distance": "6MWD",
}


METHOD_LABELS = {
    "spearman": "Spearman",
    "pearson": "Pearson",
}


# ==================================================
# AVAILABLE OPTIONS
# ==================================================

available_cohorts = (
    clinical["cohort_id"]
    .dropna()
    .drop_duplicates()
    .tolist()
)


cohort_order = [
    x
    for x in [
        "DISCOVERY",
        "C2",
        "C3",
    ]
    if x in available_cohorts
]


available_variables = (
    clinical["clinical_variable"]
    .dropna()
    .drop_duplicates()
    .tolist()
)


variable_order = [
    x
    for x in [
        "abi",
        "six_min_walk_distance",
    ]
    if x in available_variables
]


available_methods = (
    clinical["method"]
    .dropna()
    .astype(str)
    .str.lower()
    .drop_duplicates()
    .tolist()
)


method_order = [
    x
    for x in [
        "spearman",
        "pearson",
    ]
    if x in available_methods
]


CLINICAL_GENES = (
    clinical["feature_id"]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .tolist()
)


# ==================================================
# DEFAULTS
# ==================================================

default_cohort = (
    "DISCOVERY"
    if "DISCOVERY" in cohort_order
    else cohort_order[0]
)


default_variable = (
    "abi"
    if "abi" in variable_order
    else variable_order[0]
)


default_method = (
    "spearman"
    if "spearman" in method_order
    else method_order[0]
)


default_gene = (
    "GADD45A"
    if "GADD45A" in CLINICAL_GENES
    else CLINICAL_GENES[0]
)


# ==================================================
# COLORS
# ==================================================

CORRELATION_COLORSCALE = [
    [0.00, "#0000a5"],
    [0.25, "#0000d8"],
    [0.50, "#FFFAF0"],
    [0.75, "#d80000"],
    [1.00, "#a50000"],
]


NS_COLOR = "#B8B8B8"


# ==================================================
# HELPERS
# ==================================================

def format_correlation(value):

    if value is None or pd.isna(value):
        return "—"

    return f"{value:.2f}"


def format_fdr(value):

    if value is None or pd.isna(value):
        return "—"

    if value < 0.001:
        return f"{value:.1e}"

    return f"{value:.3f}"


def format_n(value):

    if value is None or pd.isna(value):
        return "—"

    return str(int(value))


def metric_card(
    label,
    value,
):

    return html.Div(
        [
            html.Div(
                label,
                style={
                    "fontSize": "12px",
                    "fontWeight": "700",
                    "marginBottom": "5px",
                },
            ),

            html.Div(
                value,
                style={
                    "fontSize": "20px",
                    "fontWeight": "600",
                },
            ),
        ],

        style={
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "padding": "12px 14px",
            "boxSizing": "border-box",
            "backgroundColor": "transparent",
        },
    )


# ==================================================
# TABLE STYLE
# ==================================================

TABLE_COLUMNS = [
    {
        "name": "Gene",
        "id": "feature_id",
    },
    {
        "name": "N",
        "id": "n",
    },
    {
        "name": "Correlation",
        "id": "correlation",
    },
    {
        "name": "FDR",
        "id": "fdr",
    },
]


TABLE_STYLE_HEADER = {
    "fontWeight": "bold",
    "backgroundColor": "#f7f7f7",
    "borderBottom": "2px solid #ddd",
    "textAlign": "left",
    "padding": "7px 8px",
}


TABLE_STYLE_CELL = {
    "fontFamily": "Arial, sans-serif",
    "fontSize": "13px",
    "padding": "7px 8px",
    "textAlign": "left",
    "border": "none",
    "borderBottom": "1px solid #eee",
}


TABLE_STYLE_CONDITIONAL = [
    {
        "if": {
            "column_id": "feature_id",
        },
        "fontWeight": "600",
        "width": "38%",
    },
    {
        "if": {
            "column_id": "n",
        },
        "width": "14%",
    },
    {
        "if": {
            "column_id": "correlation",
        },
        "width": "24%",
    },
    {
        "if": {
            "column_id": "fdr",
        },
        "width": "24%",
    },
]


# ==================================================
# PAGE
# ==================================================

layout = html.Div(
    [
        html.H1(
            "Clinical Correlations",
            style={
                "marginTop": 0,
            },
        ),

        html.P(
            "Explore gene-level associations with clinical "
            "measurements within individual cohorts."
        ),


        # ==================================================
        # CONTROLS
        # ==================================================

        html.Div(
            [
                # ------------------------------------------
                # Cohort
                # ------------------------------------------

                html.Div(
                    [
                        html.Label(
                            "Cohort",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "13px",
                            },
                        ),

                        dcc.Dropdown(
                            id="clinical-cohort",

                            options=[
                                {
                                    "label":
                                        COHORT_LABELS.get(
                                            cohort,
                                            cohort,
                                        ),

                                    "value":
                                        cohort,
                                }
                                for cohort
                                in cohort_order
                            ],

                            value=default_cohort,
                            clearable=False,
                        ),
                    ],

                    style={
                        "width": "210px",
                    },
                ),


                # ------------------------------------------
                # Clinical variable
                # ------------------------------------------

                html.Div(
                    [
                        html.Label(
                            "Clinical measurement",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "13px",
                            },
                        ),

                        dcc.Dropdown(
                            id="clinical-variable",

                            options=[
                                {
                                    "label":
                                        CLINICAL_LABELS.get(
                                            variable,
                                            variable,
                                        ),

                                    "value":
                                        variable,
                                }
                                for variable
                                in variable_order
                            ],

                            value=default_variable,
                            clearable=False,
                        ),
                    ],

                    style={
                        "width": "180px",
                    },
                ),


                # ------------------------------------------
                # Method
                # ------------------------------------------

                html.Div(
                    [
                        html.Label(
                            "Correlation method",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "13px",
                                "display": "block",
                                "marginBottom": "8px",
                            },
                        ),

                        dcc.RadioItems(
                            id="clinical-method",

                            options=[
                                {
                                    "label":
                                        METHOD_LABELS.get(
                                            method,
                                            method.title(),
                                        ),

                                    "value":
                                        method,
                                }
                                for method
                                in method_order
                            ],

                            value=default_method,

                            inline=True,

                            labelStyle={
                                "display": "inline-flex",
                                "alignItems": "center",
                                "marginRight": "20px",
                                "fontSize": "14px",
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
                        "minWidth": "240px",
                    },
                ),
            ],

            style={
                "display": "flex",
                "gap": "20px",
                "flexWrap": "wrap",
                "alignItems": "flex-end",
                "marginBottom": "28px",
            },
        ),


        # ==================================================
        # PLOT + GENE QUERY
        # ==================================================

        html.Div(
            [
                # ------------------------------------------
                # Plot
                # ------------------------------------------

                html.Div(
                    id="clinical-plot-panel",

                    style={
                        "flex": "0 1 720px",
                        "width": "720px",
                        "maxWidth": "720px",
                        "minWidth": "560px",
                    },
                ),


                # ------------------------------------------
                # Gene Query
                # ------------------------------------------

                html.Div(
                    [
                        html.H3(
                            "Gene query",

                            style={
                                "marginTop": 0,
                                "marginBottom": "12px",
                            },
                        ),

                        html.Label(
                            "Gene",

                            style={
                                "fontWeight": "bold",
                                "fontSize": "13px",
                            },
                        ),

                        dcc.Dropdown(
                            id="clinical-gene",

                            options=[
                                {
                                    "label": gene,
                                    "value": gene,
                                }
                                for gene
                                in CLINICAL_GENES
                            ],

                            value=default_gene,
                            searchable=True,
                            clearable=False,
                        ),
                        
                        html.Div(
                            id="clinical-gene-links",
                            style={
                                "display": "flex",
                                "gap": "12px",
                                "marginTop": "8px",
                                "fontSize": "12px",
                                "fontWeight": "600",
                            },
                        ),
                        
                        html.Div(
                            id="clinical-gene-context",

                            style={
                                "marginTop": "13px",
                                "marginBottom": "13px",
                                "fontSize": "13px",
                                "fontWeight": "600",
                                "color": "#607483",
                            },
                        ),

                        html.Div(
                            id="clinical-gene-metrics",
                        ),
                    ],

                    style={
                        "flex": "0 0 300px",
                        "width": "300px",
                        "maxWidth": "300px",

                        "border": "1px solid #ddd",
                        "borderRadius": "8px",

                        "padding": "18px",

                        "boxSizing": "border-box",

                        # transparent panel
                        "backgroundColor": "transparent",
                    },
                ),
            ],

            style={
                "display": "flex",
                "gap": "18px",

                # prevents Gene Query from stretching vertically
                "alignItems": "flex-start",

                "flexWrap": "wrap",

                "maxWidth": "1040px",
                "marginBottom": "26px",
            },
        ),


        # ==================================================
        # SIGNIFICANT TABLES
        # ==================================================

        html.Div(
            id="clinical-tables",
        ),
    ]
)


# ==================================================
# CALLBACK
# ==================================================

@callback(
    Output(
        "clinical-plot-panel",
        "children",
    ),

    Output(
        "clinical-gene-context",
        "children",
    ),

    Output(
        "clinical-gene-metrics",
        "children",
    ),

    Output(
        "clinical-gene-links",
        "children",
    ),

    Output(
        "clinical-tables",
        "children",
    ),

    Input(
        "clinical-cohort",
        "value",
    ),

    Input(
        "clinical-variable",
        "value",
    ),

    Input(
        "clinical-method",
        "value",
    ),

    Input(
        "clinical-gene",
        "value",
    ),
)
def update_clinical(
    cohort_id,
    clinical_variable,
    method,
    selected_gene,
):

    # ==================================================
    # LABELS
    # ==================================================

    cohort_label = (
        COHORT_LABELS.get(
            cohort_id,
            cohort_id,
        )
    )


    method_label = (
        METHOD_LABELS.get(
            method.lower(),
            method.title(),
        )
    )


    variable_label = (
        CLINICAL_LABELS.get(
            clinical_variable,
            clinical_variable,
        )
    )


    context_label = (
        f"{cohort_label} · "
        f"{method_label} · "
        f"{variable_label}"
    )


    # ==================================================
    # FILTER DATA
    # ==================================================

    data = clinical[
        (
            clinical["cohort_id"]
            == cohort_id
        )
        &
        (
            clinical["clinical_variable"]
            == clinical_variable
        )
        &
        (
            clinical["method"]
            .astype(str)
            .str.lower()
            == method.lower()
        )
    ].copy()


    if data.empty:

        no_data = html.Div(
            "No clinical correlation results are available "
            "for this selection.",

            style={
                "padding": "20px 0",
                "color": "#607483",
            },
        )

        return (
            no_data,
            context_label,
            no_data,
            "",
            no_data,
        )


    # ==================================================
    # NUMERIC VALUES
    # ==================================================

    for column in [
        "correlation",
        "fdr",
        "p_value",
        "n",
    ]:

        if column in data.columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )


    # ==================================================
    # SIGNIFICANCE
    # ==================================================

    data["significant"] = (
        data["fdr"].notna()
        &
        (
            data["fdr"]
            < 0.05
        )
    )


    data["minus_log10_fdr"] = (
        -np.log10(
            data["fdr"]
            .clip(
                lower=1e-300
            )
        )
    )


    # ==================================================
    # PLOT
    # ==================================================

    fig = go.Figure()


    # --------------------------------------------------
    # Non-significant
    # --------------------------------------------------

    ns = data[
        ~data["significant"]
    ].copy()


    fig.add_trace(
        go.Scattergl(
            x=ns["correlation"],
            y=ns["minus_log10_fdr"],

            mode="markers",

            marker=dict(
                size=6,
                color=NS_COLOR,
                opacity=0.50,
            ),

            customdata=np.column_stack(
                [
                    ns["feature_id"],
                    ns["n"],
                    ns["fdr"],
                ]
            ),

            hovertemplate=(
                "<b>%{customdata[0]}</b>"
                "<br>Correlation: %{x:.3f}"
                "<br>FDR: %{customdata[2]:.3g}"
                "<br>N: %{customdata[1]:.0f}"
                "<extra></extra>"
            ),

            name="Not significant",
        )
    )


    # --------------------------------------------------
    # Significant
    # --------------------------------------------------

    sig = data[
        data["significant"]
    ].copy()


    fig.add_trace(
        go.Scattergl(
            x=sig["correlation"],
            y=sig["minus_log10_fdr"],

            mode="markers",

            marker=dict(
                size=8,

                color=sig[
                    "correlation"
                ],

                colorscale=(
                    CORRELATION_COLORSCALE
                ),

                cmin=-1,
                cmax=1,

                opacity=0.90,

                line=dict(
                    width=0.4,
                    color="white",
                ),

                colorbar=dict(
                    title="Correlation",
                    thickness=12,
                    len=0.62,
                ),
            ),

            customdata=np.column_stack(
                [
                    sig["feature_id"],
                    sig["n"],
                    sig["fdr"],
                ]
            ),

            hovertemplate=(
                "<b>%{customdata[0]}</b>"
                "<br>Correlation: %{x:.3f}"
                "<br>FDR: %{customdata[2]:.3g}"
                "<br>N: %{customdata[1]:.0f}"
                "<extra></extra>"
            ),

            name="Significant",
            showlegend=False,
        )
    )


    # ==================================================
    # REFERENCE LINES
    # ==================================================

    fig.add_vline(
        x=0,
        line_width=1,
        line_dash="dot",
        line_color="#7a7a7a",
    )


    fig.add_hline(
        y=-np.log10(0.05),
        line_width=1,
        line_dash="dash",
        line_color="#7a7a7a",
    )


    # ==================================================
    # PLOT STYLE
    # ==================================================

    fig.update_layout(
        height=500,

        margin=dict(
            l=55,
            r=20,
            t=25,
            b=50,
        ),

        xaxis_title="Correlation",

        yaxis_title=(
            "−log10(FDR)"
        ),

        legend=dict(
            orientation="h",

            yanchor="bottom",
            y=1.01,

            xanchor="left",
            x=0,
        ),

        paper_bgcolor="white",
        plot_bgcolor="white",

        hovermode="closest",
    )


    fig.update_xaxes(
        range=[
            -1.03,
            1.03,
        ],

        zeroline=False,
    )


    fig.update_yaxes(
        rangemode="tozero",
        zeroline=False,
    )


    # ==================================================
    # PLOT PANEL
    # ==================================================

    plot_panel = html.Div(
        [
            html.H3(
                [
                    variable_label,

                    html.Span(
                        (
                            f" — {cohort_label} · "
                            f"{method_label}"
                        ),

                        style={
                            "fontWeight": "500",
                            "color": "#607483",
                        },
                    ),
                ],

                style={
                    "marginTop": 0,
                    "marginBottom": "4px",
                },
            ),

            html.P(
                "Gene-level correlations. Significant genes "
                "(FDR < 0.05) are colored by correlation; "
                "non-significant genes are shown in gray.",

                style={
                    "marginTop": 0,
                    "marginBottom": "8px",
                    "fontSize": "14px",
                },
            ),

            dcc.Graph(
                figure=fig,

                config={
                    "displaylogo": False,
                },

                style={
                    "width": "100%",
                },
            ),
        ],

        style={
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "padding": "18px",
            "width": "100%",
            "boxSizing": "border-box",
        },
    )


    # ==================================================
    # GENE QUERY
    # ==================================================

    gene_result = data[
        data["feature_id"]
        == selected_gene
    ]


    if gene_result.empty:

        gene_metrics = html.Div(
            "No correlation result is available for this gene "
            "under the current selection.",

            style={
                "color": "#607483",
                "paddingTop": "8px",
                "fontSize": "13px",
            },
        )

    else:

        gene_row = (
            gene_result.iloc[0]
        )


        gene_metrics = html.Div(
            [
                metric_card(
                    "N",
                    format_n(
                        gene_row["n"]
                    ),
                ),

                metric_card(
                    "Correlation",
                    format_correlation(
                        gene_row[
                            "correlation"
                        ]
                    ),
                ),

                metric_card(
                    "FDR",
                    format_fdr(
                        gene_row["fdr"]
                    ),
                ),
            ],

            style={
                "display": "grid",
                "gridTemplateColumns": "1fr",
                "gap": "9px",
            },
        )


    # ==================================================
    # SIGNIFICANT GENES
    # ==================================================

    significant = data[
        data["significant"]
    ].copy()


    # --------------------------------------------------
    # Top negative
    # --------------------------------------------------

    negative = (
        significant[
            significant[
                "correlation"
            ]
            < 0
        ]
        .sort_values(
            "correlation",
            ascending=True,
        )
        .head(20)
        .copy()
    )


    # --------------------------------------------------
    # Top positive
    # --------------------------------------------------

    positive = (
        significant[
            significant[
                "correlation"
            ]
            > 0
        ]
        .sort_values(
            "correlation",
            ascending=False,
        )
        .head(20)
        .copy()
    )


    # ==================================================
    # TABLE DATA
    # ==================================================

    def make_table_data(df):

        output = []

        for _, row in df.iterrows():

            output.append(
                {
                    "feature_id":
                        row[
                            "feature_id"
                        ],

                    "n":
                        format_n(
                            row["n"]
                        ),

                    "correlation":
                        format_correlation(
                            row[
                                "correlation"
                            ]
                        ),

                    "fdr":
                        format_fdr(
                            row["fdr"]
                        ),
                }
            )

        return output


    negative_data = (
        make_table_data(
            negative
        )
    )


    positive_data = (
        make_table_data(
            positive
        )
    )


    # ==================================================
    # TABLE PANEL
    # ==================================================

    tables = html.Div(
        [
            html.H3(
                [
                    "Significant genes",

                    html.Span(
                        (
                            f" — {cohort_label} · "
                            f"{method_label} · "
                            f"{variable_label}"
                        ),

                        style={
                            "fontWeight": "500",
                            "color": "#607483",
                        },
                    ),
                ],

                style={
                    "marginTop": 0,
                    "marginBottom": "5px",
                },
            ),

            html.P(
                "Top significant genes ranked separately "
                "by negative and positive correlation.",

                style={
                    "marginTop": 0,
                    "marginBottom": "15px",
                    "fontSize": "14px",
                },
            ),


            # ==================================================
            # TWO TABLES
            # ==================================================

            html.Div(
                [
                    # ------------------------------------------
                    # Negative
                    # ------------------------------------------

                    html.Div(
                        [
                            html.H4(
                                "Top negative",

                                style={
                                    "marginTop": 0,
                                    "marginBottom": "8px",
                                    "color": "#0000a5",
                                },
                            ),

                            (
                                dash_table.DataTable(
                                    columns=TABLE_COLUMNS,
                                    data=negative_data,

                                    page_action="none",

                                    style_table={
                                        "overflowX": "auto",
                                        "width": "100%",
                                    },

                                    style_header=(
                                        TABLE_STYLE_HEADER
                                    ),

                                    style_cell=(
                                        TABLE_STYLE_CELL
                                    ),

                                    style_cell_conditional=(
                                        TABLE_STYLE_CONDITIONAL
                                    ),
                                )

                                if negative_data

                                else html.Div(
                                    "No significant negative correlations.",

                                    style={
                                        "padding": "14px 0",
                                        "color": "#607483",
                                    },
                                )
                            ),
                        ],

                        style={
                            "flex": "1 1 390px",
                            "minWidth": "330px",
                        },
                    ),


                    # ------------------------------------------
                    # Positive
                    # ------------------------------------------

                    html.Div(
                        [
                            html.H4(
                                "Top positive",

                                style={
                                    "marginTop": 0,
                                    "marginBottom": "8px",
                                    "color": "#a50000",
                                },
                            ),

                            (
                                dash_table.DataTable(
                                    columns=TABLE_COLUMNS,
                                    data=positive_data,

                                    page_action="none",

                                    style_table={
                                        "overflowX": "auto",
                                        "width": "100%",
                                    },

                                    style_header=(
                                        TABLE_STYLE_HEADER
                                    ),

                                    style_cell=(
                                        TABLE_STYLE_CELL
                                    ),

                                    style_cell_conditional=(
                                        TABLE_STYLE_CONDITIONAL
                                    ),
                                )

                                if positive_data

                                else html.Div(
                                    "No significant positive correlations.",

                                    style={
                                        "padding": "14px 0",
                                        "color": "#607483",
                                    },
                                )
                            ),
                        ],

                        style={
                            "flex": "1 1 390px",
                            "minWidth": "330px",
                        },
                    ),
                ],

                style={
                    "display": "flex",
                    "gap": "18px",
                    "alignItems": "flex-start",
                    "flexWrap": "wrap",
                },
            ),


            # ==================================================
            # N EXPLANATION
            # ==================================================

            html.P(
                [
                    html.Strong("N"),
                    " is the number of participants with both "
                    "an available gene-expression value and an "
                    "available clinical measurement used for "
                    "that gene-level correlation.",
                ],

                style={
                    "fontSize": "12px",
                    "color": "#607483",
                    "marginTop": "14px",
                    "marginBottom": 0,
                },
            ),
        ],

        style={
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "padding": "18px",
            "maxWidth": "1000px",
            "boxSizing": "border-box",
        },
    )

    gene_links = html.Div(
        [
            html.A(
                "GeneCards ↗",
                href=(
                    "https://www.genecards.org/"
                    f"cgi-bin/carddisp.pl?gene={selected_gene}"
                ),
                target="_blank",
                rel="noopener noreferrer",
                style={
                    "textDecoration": "none",
                    "color": "var(--lab-blue)",
                },
            ),
    
            html.A(
                "Human Protein Atlas ↗",
                href=(
                    "https://www.proteinatlas.org/"
                    f"search/{selected_gene}"
                ),
                target="_blank",
                rel="noopener noreferrer",
                style={
                    "textDecoration": "none",
                    "color": "var(--lab-blue)",
                },
            ),
        ],
    
        style={
            "display": "flex",
            "gap": "12px",
            "flexWrap": "wrap",
        },
    )


    return (
        plot_panel,
        context_label,
        gene_metrics,
        gene_links,
        tables,
    )