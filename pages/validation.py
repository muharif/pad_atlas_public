import dash
from dash import html, dcc, Input, Output, callback
import numpy as np
import plotly.express as px

from pad_atlas_public.utils.loaders import load_table


dash.register_page(
    __name__,
    path="/validation",
    name="Cross-cohort Validation",
)


# ==================================================
# LOAD DATA
# ==================================================

meta = load_table("mrna_meta")


COMPARISON_LABELS = {
    "IC_VS_HC": "S-II / IC vs HC",
    "CLI_VS_HC": "S-IV / CLI vs HC",
}

VALIDATION_LABELS = {
    "c2_lfc": "Cohort 2",
    "c3_lfc": "Cohort 3",
}


# ==================================================
# HELPERS
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
            "minWidth": "155px",
        },
    )


# ==================================================
# LAYOUT
# ==================================================

layout = html.Div(
    [
        html.H1(
            "Cross-cohort Validation",
            style={"marginTop": 0},
        ),

        html.P(
            "Compare skeletal muscle differential-expression effects "
            "across the Discovery and validation cohorts."
        ),

        # --------------------------------------------------
        # Controls
        # --------------------------------------------------

        html.Div(
            [
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
                            id="validation-comparison",
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

                html.Div(
                    [
                        html.Label(
                            "Validation cohort",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "13px",
                            },
                        ),

                        dcc.Dropdown(
                            id="validation-cohort",
                            options=[
                                {
                                    "label": "Cohort 2",
                                    "value": "c2_lfc",
                                },
                                {
                                    "label": "Cohort 3",
                                    "value": "c3_lfc",
                                },
                            ],
                            value="c2_lfc",
                            clearable=False,
                        ),
                    ],
                    style={"width": "220px"},
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
            id="validation-content"
        ),
    ]
)


# ==================================================
# CALLBACK
# ==================================================

@callback(
    Output(
        "validation-content",
        "children",
    ),
    Input(
        "validation-comparison",
        "value",
    ),
    Input(
        "validation-cohort",
        "value",
    ),
)
def update_validation(
    comparison_id,
    validation_column,
):

    df = meta[
        meta["comparison_id"] == comparison_id
    ].copy()


    # ==================================================
    # SUMMARY
    # ==================================================

    n_tested = len(df)

    n_three_cohorts = int(
        (df["n_cohorts"] == 3).sum()
    )

    n_same_direction = int(
        (
            (df["n_cohorts"] == 3)
            &
            (df["same_direction"] == True)
        ).sum()
    )

    n_consensus_fe = int(
        df["consensus_fe"].fillna(False).sum()
    )

    n_consensus_re = int(
        df["consensus_re"].fillna(False).sum()
    )


    # ==================================================
    # PLOT DATA
    # ==================================================

    plot_df = df[
        [
            "feature_id",
            "discovery_lfc",
            validation_column,
            "meta_lfc_fe",
            "meta_fdr_fe",
            "same_direction",
            "consensus_fe",
            "i2",
        ]
    ].dropna(
        subset=[
            "discovery_lfc",
            validation_column,
        ]
    ).copy()


    plot_df["consensus_status"] = np.where(
        plot_df["consensus_fe"],
        "Strict consensus",
        "Not strict consensus",
    )


    # ==================================================
    # SCATTER
    # ==================================================

    validation_label = (
        VALIDATION_LABELS[
            validation_column
        ]
    )

    fig = px.scatter(
        plot_df,
        x="discovery_lfc",
        y=validation_column,
        color="consensus_status",

        hover_name="feature_id",

        hover_data={
            "discovery_lfc": ":.3f",
            validation_column: ":.3f",
            "meta_lfc_fe": ":.3f",
            "meta_fdr_fe": ":.3e",
            "i2": ":.1f",
            "same_direction": True,
            "consensus_status": False,
        },

        labels={
            "discovery_lfc":
                "Discovery log2 fold change",

            validation_column:
                f"{validation_label} log2 fold change",

            "meta_lfc_fe":
                "Meta log2 fold change",

            "meta_fdr_fe":
                "Meta FDR",

            "i2":
                "I²",

            "same_direction":
                "Same direction",

            "consensus_status":
                "",
        },
    )


    # --------------------------------------------------
    # Diagonal y = x
    # --------------------------------------------------

    values = np.concatenate(
        [
            plot_df["discovery_lfc"].to_numpy(),
            plot_df[validation_column].to_numpy(),
        ]
    )

    values = values[
        np.isfinite(values)
    ]

    if len(values) > 0:

        lower = values.min()
        upper = values.max()

        fig.add_shape(
            type="line",
            x0=lower,
            y0=lower,
            x1=upper,
            y1=upper,
            line=dict(
                dash="dash",
            ),
        )


    # Zero reference lines
    fig.add_hline(
        y=0,
        line_dash="dot",
    )

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
        height=600,
        margin=dict(
            l=50,
            r=20,
            t=30,
            b=50,
        ),
        legend_title_text="",
    )


    # ==================================================
    # RETURN
    # ==================================================

    return html.Div(
        [
            # ------------------------------------------
            # Summary cards
            # ------------------------------------------

            html.Div(
                [
                    summary_card(
                        n_tested,
                        "Genes evaluated",
                    ),

                    summary_card(
                        n_three_cohorts,
                        "Present in 3 cohorts",
                    ),

                    summary_card(
                        n_same_direction,
                        "Same direction",
                    ),

                    summary_card(
                        n_consensus_fe,
                        "Strict FE consensus",
                    ),

                    summary_card(
                        n_consensus_re,
                        "RE consensus",
                    ),
                ],
                style={
                    "display": "flex",
                    "gap": "12px",
                    "flexWrap": "wrap",
                    "marginBottom": "24px",
                },
            ),

            # ------------------------------------------
            # Concordance plot
            # ------------------------------------------

            html.Div(
                [
                    html.H3(
                        f"Discovery vs {validation_label}",
                        style={
                            "marginTop": 0,
                            "marginBottom": "4px",
                        },
                    ),

                    html.P(
                        f"{COMPARISON_LABELS[comparison_id]}. "
                        "The dashed diagonal represents equal "
                        "effect sizes in both cohorts.",
                        style={
                            "marginTop": 0,
                            "marginBottom": "10px",
                        },
                    ),

                    dcc.Graph(
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