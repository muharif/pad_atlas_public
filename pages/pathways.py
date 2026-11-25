import dash
from dash import html, dcc, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go

from pad_atlas_public.utils.loaders import load_table


dash.register_page(
    __name__,
    path="/pathways",
    name="Pathway Enrichment",
)


results = load_table("pathway_results")
concordance = load_table("pathway_concordance")


COHORT_LABELS = {
    "DISCOVERY": "Discovery",
    "C2": "Cohort 2",
    "C3": "Cohort 3",
}

COMPARISON_LABELS = {
    "IC_VS_HC": "S-II / IC vs HC",
    "CLI_VS_HC": "S-IV / CLI vs HC",
}


def card(value, label):

    return html.Div(
        [
            html.Div(
                str(value),
                style={
                    "fontSize": "26px",
                    "fontWeight": "bold",
                },
            ),
            html.Div(label),
        ],
        style={
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "padding": "16px",
            "minWidth": "145px",
        },
    )


layout = html.Div(
    [
        html.H1(
            "Pathways",
            style={"marginTop": 0},
        ),

        html.P(
            "Explore cohort-specific pathway enrichment and "
            "cross-cohort directional concordance."
        ),

        html.Div(
            [
                html.Div(
                    [
                        html.Label(
                            "Cohort",
                            style={"fontWeight": "bold"},
                        ),

                        dcc.Dropdown(
                            id="pathway-cohort",
                            options=[
                                {
                                    "label": label,
                                    "value": value,
                                }
                                for value, label
                                in COHORT_LABELS.items()
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
                                "display": "block",
                                "marginBottom": "8px",
                            },
                        ),
                
                        dcc.RadioItems(
                            id="pathway-comparison",
                
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

                html.Div(
                    [
                        html.Label(
                            "Database",
                            style={"fontWeight": "bold"},
                        ),

                        dcc.Dropdown(
                            id="pathway-database",
                            options=[
                                {
                                    "label": db,
                                    "value": db,
                                }
                                for db in sorted(
                                    results["database"]
                                    .dropna()
                                    .unique()
                                )
                            ],
                            value="KEGG",
                            clearable=False,
                        ),
                    ],
                    style={"width": "180px"},
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
            id="pathway-content"
        ),
    ]
)


@callback(
    Output(
        "pathway-content",
        "children",
    ),
    Input(
        "pathway-cohort",
        "value",
    ),
    Input(
        "pathway-comparison",
        "value",
    ),
    Input(
        "pathway-database",
        "value",
    ),
)
def update_pathways(
    cohort_id,
    comparison_id,
    database,
):

    df = results[
        (results["cohort_id"] == cohort_id)
        &
        (results["comparison_id"] == comparison_id)
        &
        (results["database"] == database)
    ].copy()

    sig = df[
        df["fdr"].notna()
        &
        (df["fdr"] < 0.05)
    ].copy()

    direction_upper = (
        sig["direction"]
        .astype(str)
        .str.upper()
    )

    n_up = int(
        (direction_upper == "UP").sum()
    )

    n_down = int(
        (direction_upper == "DOWN").sum()
    )

    conc = concordance[
        (concordance["comparison_id"] == comparison_id)
        &
        (concordance["database"] == database)
    ].copy()

    validated = conc[
        conc["discovery_fdr"].notna()
        &
        (conc["discovery_fdr"] < 0.05)
        &
        (
            conc["validation_sign_concordant"]
            == True
        )
    ]

    if sig.empty:

        fig = go.Figure()

        fig.add_annotation(
            text="No pathways with FDR < 0.05",
            x=0.5,
            y=0.5,
            showarrow=False,
            xref="paper",
            yref="paper",
        )

        fig.update_layout(
            height=450,
        )

    else:

        top = (
            sig
            .sort_values("fdr")
            .head(25)
            .sort_values("stats")
        )

        fig = px.bar(
            top,
            x="stats",
            y="pathway_name",
            color="direction",
            orientation="h",
            hover_data={
                "fdr": ":.3e",
                "n_genes": True,
                "pathway_id": True,
                "stats": ":.3f",
            },
            labels={
                "stats": "Enrichment statistic",
                "pathway_name": "",
                "direction": "Direction",
                "fdr": "FDR",
                "n_genes": "Genes",
                "pathway_id": "Pathway ID",
            },
        )

        fig.update_layout(
            height=max(
                500,
                len(top) * 25 + 150,
            ),
            margin=dict(
                l=40,
                r=20,
                t=20,
                b=40,
            ),
        )

    table_df = (
        sig
        .sort_values("fdr")
        .head(100)
    )

    table_data = table_df[
        [
            "pathway_name",
            "n_genes",
            "stats",
            "fdr",
            "direction",
        ]
    ].to_dict("records")

    return html.Div(
        [
            html.Div(
                [
                    card(
                        len(df),
                        "Pathways tested",
                    ),
                    card(
                        len(sig),
                        "FDR < 0.05",
                    ),
                    card(
                        n_up,
                        "Up",
                    ),
                    card(
                        n_down,
                        "Down",
                    ),
                    card(
                        len(validated),
                        "Discovery pathways direction-concordant",
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
                        style={"marginTop": 0},
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
                    "maxWidth": "1100px",
                    "marginBottom": "20px",
                },
            ),

            html.Div(
                [
                    html.H3(
                        "Significant pathways",
                        style={"marginTop": 0},
                    ),

                    dash_table.DataTable(
                        columns=[
                            {
                                "name": "Pathway",
                                "id": "pathway_name",
                            },
                            {
                                "name": "Genes",
                                "id": "n_genes",
                            },
                            {
                                "name": "Statistic",
                                "id": "stats",
                            },
                            {
                                "name": "FDR",
                                "id": "fdr",
                            },
                            {
                                "name": "Direction",
                                "id": "direction",
                            },
                        ],
                        data=table_data,
                        sort_action="native",
                        page_size=20,
                        style_table={
                            "overflowX": "auto",
                        },
                        style_header={
                            "fontWeight": "bold",
                            "backgroundColor": "#f7f7f7",
                        },
                        style_cell={
                            "padding": "9px",
                            "textAlign": "left",
                            "border": "none",
                            "borderBottom":
                                "1px solid #eee",
                        },
                    ),
                ],
                style={
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "maxWidth": "1100px",
                },
            ),
        ]
    )