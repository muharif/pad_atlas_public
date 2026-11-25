import dash
from dash import (
    html,
    dcc,
    Input,
    Output,
    callback,
    dash_table,
)
import plotly.express as px

from pad_atlas_public.utils.loaders import load_table


dash.register_page(
    __name__,
    path="/senescence",
    name="Senescence",
)


# ==================================================
# LOAD DATA
# ==================================================

senescence = load_table(
    "senescence_consensus"
)


COMPARISON_LABELS = {
    "IC_VS_HC": "S-II / IC vs HC",
    "CLI_VS_HC": "S-IV / CLI vs HC",
}


# ==================================================
# HELPERS
# ==================================================

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


# ==================================================
# LAYOUT
# ==================================================

layout = html.Div(
    [
        html.H1(
            "Cellular Senescence",
            style={
                "marginTop": 0,
            },
        ),

        html.P(
            "Senescence genes selected using the strict "
            "cross-cohort fixed-effect consensus criterion."
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
                                "display": "block",
                                "marginBottom": "8px",
                            },
                        ),

                        dcc.RadioItems(
                            id="senescence-comparison",

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
                            "Senescence gene set",
                            style={
                                "fontWeight": "bold",
                            },
                        ),

                        dcc.Dropdown(
                            id="senescence-source",
                            options=[
                                {
                                    "label": "All sources",
                                    "value": "all",
                                },
                                {
                                    "label": "SenMayo",
                                    "value": "senmayo",
                                },
                                {
                                    "label": "KEGG",
                                    "value": "kegg",
                                },
                                {
                                    "label": "Senepy",
                                    "value": "senepy",
                                },
                                {
                                    "label": "≥ 2 sources",
                                    "value": "multi",
                                },
                                {
                                    "label": "All 3 sources",
                                    "value": "all3",
                                },
                            ],
                            value="all",
                            clearable=False,
                        ),
                    ],
                    style={
                        "width": "240px",
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
            id="senescence-content"
        ),
    ]
)


# ==================================================
# CALLBACK
# ==================================================

@callback(
    Output(
        "senescence-content",
        "children",
    ),
    Input(
        "senescence-comparison",
        "value",
    ),
    Input(
        "senescence-source",
        "value",
    ),
)
def update_senescence(
    comparison_id,
    source,
):

    # --------------------------------------------------
    # Selected comparison
    # --------------------------------------------------

    df = senescence[
        senescence["comparison_id"]
        == comparison_id
    ].copy()


    # --------------------------------------------------
    # Source filtering
    # --------------------------------------------------

    if source == "senmayo":

        df = df[
            df["in_senmayo"] == True
        ]

    elif source == "kegg":

        df = df[
            df["in_kegg"] == True
        ]

    elif source == "senepy":

        df = df[
            df["in_senepy"] == True
        ]

    elif source == "multi":

        df = df[
            df["n_sources"] >= 2
        ]

    elif source == "all3":

        df = df[
            df["n_sources"] == 3
        ]


    # --------------------------------------------------
    # Meta-analysis direction
    # --------------------------------------------------

    df["meta_direction"] = "NS"

    df.loc[
        df["meta_lfc_fe"] > 0,
        "meta_direction",
    ] = "Up"

    df.loc[
        df["meta_lfc_fe"] < 0,
        "meta_direction",
    ] = "Down"


    # --------------------------------------------------
    # Summary counts
    # --------------------------------------------------

    n_total = len(df)

    n_up = int(
        (
            df["meta_direction"] == "Up"
        ).sum()
    )

    n_down = int(
        (
            df["meta_direction"] == "Down"
        ).sum()
    )

    n_senmayo = int(
        df["in_senmayo"]
        .fillna(False)
        .sum()
    )

    n_kegg = int(
        df["in_kegg"]
        .fillna(False)
        .sum()
    )

    n_senepy = int(
        df["in_senepy"]
        .fillna(False)
        .sum()
    )


    # --------------------------------------------------
    # Top genes for bar plot
    # --------------------------------------------------

    top = (
        df
        .sort_values(
            "meta_fdr_fe"
        )
        .head(30)
        .sort_values(
            "meta_lfc_fe"
        )
    )


    # --------------------------------------------------
    # Figure
    # --------------------------------------------------

    fig = px.bar(
        top,
        x="meta_lfc_fe",
        y="feature_id",
        color="meta_direction",
        orientation="h",

        hover_data={
            "meta_fdr_fe": ":.2e",
            "senescence_sources": True,
            "n_sources": True,
        },

        labels={
            "meta_lfc_fe":
                "Fixed-effect meta log2 fold change",

            "feature_id":
                "",

            "meta_direction":
                "Direction",

            "meta_fdr_fe":
                "Meta FDR",

            "senescence_sources":
                "Sources",

            "n_sources":
                "N sources",
        },
    )

    fig.add_vline(
        x=0,
        line_dash="dot",
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
        legend_title_text="",
    )


    # --------------------------------------------------
    # Table data
    # --------------------------------------------------

    table_df = (
        df
        .sort_values(
            "meta_fdr_fe"
        )
        [
            [
                "feature_id",
                "senescence_sources",
                "n_sources",
                "meta_lfc_fe",
                "meta_fdr_fe",
                "meta_direction",
            ]
        ]
        .copy()
    )

    table_data = table_df.to_dict(
        "records"
    )


    # --------------------------------------------------
    # Return layout
    # --------------------------------------------------

    return html.Div(
        [
            # ==========================================
            # Summary cards
            # ==========================================

            html.Div(
                [
                    card(
                        n_total,
                        "Consensus senescence genes",
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
                        n_senmayo,
                        "SenMayo",
                    ),

                    card(
                        n_kegg,
                        "KEGG",
                    ),

                    card(
                        n_senepy,
                        "Senepy",
                    ),
                ],
                style={
                    "display": "flex",
                    "gap": "12px",
                    "flexWrap": "wrap",
                    "marginBottom": "24px",
                },
            ),

            # ==========================================
            # Meta-effect plot
            # ==========================================

            html.Div(
                [
                    html.H3(
                        COMPARISON_LABELS[
                            comparison_id
                        ],
                        style={
                            "marginTop": 0,
                            "marginBottom": "5px",
                        },
                    ),

                    html.P(
                        "Strict cross-cohort consensus "
                        "senescence genes ranked by "
                        "fixed-effect meta-analysis FDR.",
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
                    "marginBottom": "20px",
                    "boxSizing": "border-box",
                },
            ),

            # ==========================================
            # Consensus gene table
            # ==========================================

            html.Div(
                [
                    html.H3(
                        "Consensus genes",
                        style={
                            "marginTop": 0,
                            "marginBottom": "5px",
                        },
                    ),

                    html.P(
                        "Only genes passing the manuscript "
                        "strict cross-cohort consensus criterion "
                        "are included.",
                        style={
                            "marginTop": 0,
                            "marginBottom": "15px",
                        },
                    ),

                    dash_table.DataTable(
                        columns=[
                            {
                                "name": "Gene",
                                "id": "feature_id",
                            },

                            {
                                "name":
                                    "Senescence sources",
                                "id":
                                    "senescence_sources",
                            },

                            {
                                "name": "N sources",
                                "id": "n_sources",
                                "type": "numeric",
                            },

                            {
                                "name": "Meta LFC",
                                "id": "meta_lfc_fe",
                                "type": "numeric",
                                "format": {
                                    "specifier": ".3f"
                                },
                            },

                            {
                                "name": "Meta FDR",
                                "id": "meta_fdr_fe",
                                "type": "numeric",
                                "format": {
                                    "specifier": ".3e"
                                },
                            },

                            {
                                "name": "Direction",
                                "id": "meta_direction",
                            },
                        ],

                        data=table_data,

                        sort_action="native",

                        filter_action="native",

                        page_action="native",

                        page_size=20,

                        style_table={
                            "overflowX": "auto",
                            "width": "100%",
                        },

                        style_header={
                            "fontWeight": "bold",
                            "backgroundColor": "#f7f7f7",
                            "borderBottom":
                                "2px solid #ddd",
                            "textAlign": "left",
                            "padding": "10px",
                        },

                        style_cell={
                            "fontFamily":
                                "Arial, sans-serif",
                            "fontSize": "14px",
                            "padding": "10px",
                            "textAlign": "left",
                            "border": "none",
                            "borderBottom":
                                "1px solid #eee",
                            "minWidth": "90px",
                            "maxWidth": "260px",
                        },

                        style_cell_conditional=[
                            {
                                "if": {
                                    "column_id":
                                        "feature_id"
                                },
                                "fontWeight": "600",
                            },

                            {
                                "if": {
                                    "column_id":
                                        "senescence_sources"
                                },
                                "minWidth": "180px",
                            },
                        ],
                    ),
                ],
                style={
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "maxWidth": "1100px",
                    "boxSizing": "border-box",
                },
            ),
        ]
    )