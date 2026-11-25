import dash
from dash import html, dcc, Input, Output, callback
import numpy as np
import plotly.express as px

from pad_atlas_public.utils.loaders import load_table


dash.register_page(
    __name__,
    path="/differential-expression",
    name="Differential Expression",
)


# ==================================================
# LOAD DATA
# ==================================================

de = load_table("mrna_deseq2")


COHORT_LABELS = {
    "DISCOVERY": "Discovery",
    "C2": "Cohort 2",
    "C3": "Cohort 3",
}

COMPARISON_LABELS = {
    "IC_VS_HC": "S-II / IC vs HC",
    "CLI_VS_HC": "S-IV / CLI vs HC",
}


# ==================================================
# HELPER
# ==================================================

def summary_card(value, label):

    return html.Div(
        [
            html.Div(
                f"{value:,}",
                style={
                    "fontSize": "28px",
                    "fontWeight": "bold",
                },
            ),

            html.Div(label),
        ],
        style={
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "padding": "16px",
            "minWidth": "140px",
        },
    )


# ==================================================
# LAYOUT
# ==================================================

layout = html.Div(
    [
        html.H1(
            "Differential Expression",
            style={"marginTop": 0},
        ),

        html.P(
            "Explore cohort-specific skeletal muscle differential "
            "expression results."
        ),

        # ------------------------------------------
        # Controls
        # ------------------------------------------

        html.Div(
            [
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
                            id="de-cohort-selector",
                            options=[
                                {
                                    "label": "Discovery",
                                    "value": "DISCOVERY",
                                },
                                {
                                    "label": "Cohort 2",
                                    "value": "C2",
                                },
                                {
                                    "label": "Cohort 3",
                                    "value": "C3",
                                },
                            ],
                            value="DISCOVERY",
                            clearable=False,
                        ),
                    ],
                    style={"width": "220px"},
                ),

                html.Div(
                    [
                        html.Label(
                            "Comparison",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "13px",
                            },
                        ),

                        dcc.Dropdown(
                            id="de-comparison-selector",
                            options=[
                                {
                                    "label": "S-II / IC vs HC",
                                    "value": "IC_VS_HC",
                                },
                                {
                                    "label": "S-IV / CLI vs HC",
                                    "value": "CLI_VS_HC",
                                },
                            ],
                            value="CLI_VS_HC",
                            clearable=False,
                        ),
                    ],
                    style={"width": "260px"},
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
            id="de-content"
        ),
    ]
)


# ==================================================
# CALLBACK
# ==================================================

@callback(
    Output(
        "de-content",
        "children",
    ),
    Input(
        "de-cohort-selector",
        "value",
    ),
    Input(
        "de-comparison-selector",
        "value",
    ),
)
def update_de_page(
    cohort_id,
    comparison_id,
):

    df = de[
        (de["cohort_id"] == cohort_id)
        &
        (de["comparison_id"] == comparison_id)
    ].copy()

    # ----------------------------------------------
    # Significance
    # ----------------------------------------------

    df["significant"] = (
        df["fdr"].notna()
        &
        (df["fdr"] < 0.05)
    )

    df["status"] = "Not significant"

    df.loc[
        df["significant"]
        &
        (df["log2_fold_change"] > 0),
        "status",
    ] = "Up"

    df.loc[
        df["significant"]
        &
        (df["log2_fold_change"] < 0),
        "status",
    ] = "Down"


    # ----------------------------------------------
    # -log10(FDR)
    # ----------------------------------------------

    df["minus_log10_fdr"] = np.nan

    valid = (
        df["fdr"].notna()
        &
        (df["fdr"] >= 0)
    )

    df.loc[
        valid,
        "minus_log10_fdr",
    ] = -np.log10(
        df.loc[
            valid,
            "fdr",
        ].clip(lower=1e-300)
    )


    # ----------------------------------------------
    # Counts
    # ----------------------------------------------

    n_total = len(df)

    n_sig = int(
        df["significant"].sum()
    )

    n_up = int(
        (
            df["status"] == "Up"
        ).sum()
    )

    n_down = int(
        (
            df["status"] == "Down"
        ).sum()
    )


    # ----------------------------------------------
    # Volcano
    # ----------------------------------------------

    fig = px.scatter(
        df,
        x="log2_fold_change",
        y="minus_log10_fdr",
        color="status",

        category_orders={
            "status": [
                "Not significant",
                "Down",
                "Up",
            ]
        },

        hover_name="feature_id",

        hover_data={
            "log2_fold_change": ":.3f",
            "fdr": ":.3e",
            "base_mean": ":.2f",
            "minus_log10_fdr": False,
            "status": True,
        },

        labels={
            "log2_fold_change": "log2 fold change",
            "minus_log10_fdr": "-log10(FDR)",
            "status": "",
            "base_mean": "Base mean",
            "fdr": "FDR",
        },
    )


    # FDR = 0.05 line
    fig.add_hline(
        y=-np.log10(0.05),
        line_dash="dash",
        annotation_text="FDR = 0.05",
        annotation_position="top right",
    )


    # zero fold-change line
    fig.add_vline(
        x=0,
        line_dash="dot",
    )


    fig.update_traces(
        marker=dict(
            size=6,
            opacity=0.65,
        )
    )


    fig.update_layout(
        height=560,
        margin=dict(
            l=40,
            r=20,
            t=30,
            b=40,
        ),
        legend_title_text="",
    )


    # ----------------------------------------------
    # RETURN
    # ----------------------------------------------

    return html.Div(
        [
            html.Div(
                [
                    summary_card(
                        n_total,
                        "Genes tested",
                    ),

                    summary_card(
                        n_sig,
                        "FDR < 0.05",
                    ),

                    summary_card(
                        n_up,
                        "Significant up",
                    ),

                    summary_card(
                        n_down,
                        "Significant down",
                    ),
                ],
                style={
                    "display": "flex",
                    "gap": "12px",
                    "flexWrap": "wrap",
                    "marginBottom": "24px",
                },
            ),

            html.Div(
                [
                    html.H3(
                        f"{COHORT_LABELS[cohort_id]} — "
                        f"{COMPARISON_LABELS[comparison_id]}",
                        style={
                            "marginTop": 0,
                            "marginBottom": "4px",
                        },
                    ),

                    html.P(
                        "Hover over a point to inspect the gene.",
                        style={
                            "marginTop": 0,
                            "marginBottom": "10px",
                        },
                    ),

                    dcc.Graph(
                        id="de-volcano",
                        figure=fig,
                        config={
                            "displaylogo": False,
                        },
                    ),
                ],
                style={
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "maxWidth": "950px",
                    "margin": "0",
                },
            ),
        ]
    )