import dash

from dash import (
    html,
    dcc,
    Input,
    Output,
    callback,
    dash_table,
)

import pandas as pd
import plotly.graph_objects as go

from pad_atlas_public.utils.loaders import (
    load_table,
    DATA_DIR,
)


dash.register_page(
    __name__,
    path="/overview",
    name="Overview",
)


# ============================================================
# LOAD DATA
# ============================================================




TABLE1_PATH = (
    DATA_DIR
    / "overview_table1.parquet"
)


if TABLE1_PATH.exists():

    table1 = pd.read_parquet(
        TABLE1_PATH
    )

else:

    table1 = pd.DataFrame()


# ============================================================
# LABELS
# ============================================================

COHORT_LABELS = {
    "DISCOVERY": "Discovery",
    "C2": "Cohort 2",
    "C3": "Cohort 3",
}


COHORT_ORDER = [
    "Discovery",
    "Cohort 2",
    "Cohort 3",
]


GROUP_LABELS = {
    "HC": "HC",
    "IC": "S-II",
    "CLI": "S-IV",
}


GROUP_ORDER = [
    "HC",
    "IC",
    "CLI",
]


GROUP_COLORS = {
    "HC": "#5667F2",
    "IC": "#F0523A",
    "CLI": "#08C79A",
}


# ============================================================
# COHORT COMPOSITION
# ============================================================

composition = load_table("cohort_composition")


composition[
    "cohort_label"
] = (
    composition[
        "cohort_id"
    ]
    .map(
        COHORT_LABELS
    )
)


composition[
    "group_label"
] = (
    composition[
        "group_id"
    ]
    .map(
        GROUP_LABELS
    )
)


# ============================================================
# BUILD COMPOSITION FIGURE
# ============================================================

composition_fig = go.Figure()


for group_id in GROUP_ORDER:

    group_data = (
        composition[
            composition[
                "group_id"
            ]
            == group_id
        ]
        .copy()
    )


    # Ensure cohort ordering
    group_data[
        "cohort_label"
    ] = pd.Categorical(
        group_data[
            "cohort_label"
        ],
        categories=[
            "Discovery",
            "Cohort 2",
            "Cohort 3",
        ],
        ordered=True,
    )


    group_data = (
        group_data
        .sort_values(
            "cohort_label"
        )
    )


    composition_fig.add_trace(
        go.Bar(
            x=group_data[
                "cohort_label"
            ],

            y=group_data[
                "n"
            ],

            name=GROUP_LABELS[
                group_id
            ],

            marker_color=GROUP_COLORS[
                group_id
            ],

            text=group_data[
                "n"
            ],

            textposition="outside",

            cliponaxis=False,

            hovertemplate=(
                "<b>%{x}</b>"
                "<br>"
                + GROUP_LABELS[
                    group_id
                ]
                + ": %{y}"
                "<extra></extra>"
            ),
        )
    )


composition_fig.update_layout(
    barmode="group",

    height=360,

    margin=dict(
        l=55,
        r=20,
        t=20,
        b=50,
    ),

    xaxis_title=None,

    yaxis_title=(
        "Number of participants"
    ),

    legend_title=(
        "PAD group"
    ),

    legend=dict(
        x=1.01,
        y=1,
        xanchor="left",
        yanchor="top",
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",

    bargap=0.28,
    bargroupgap=0.03,
)


composition_fig.update_xaxes(
    showgrid=False,
    categoryorder="array",
    categoryarray=[
        "Discovery",
        "Cohort 2",
        "Cohort 3",
    ],
)


composition_fig.update_yaxes(
    gridcolor="#E3E9EE",
    rangemode="tozero",
)


# ============================================================
# HELPERS
# ============================================================

def get_total_n(
    cohort,
    group,
):

    if table1.empty:
        return None


    x = table1[
        table1["cohort"]
        == cohort
    ]


    if x.empty:
        return None


    column = (
        f"{group}_n_total"
    )


    if column not in x.columns:
        return None


    values = (
        x[column]
        .dropna()
    )


    if values.empty:
        return None


    return int(
        values.iloc[0]
    )


def make_group_header(
    cohort,
    group,
):

    n = get_total_n(
        cohort,
        group,
    )


    if n is None:
        return group


    return (
        f"{group} (N={n})"
    )


# ============================================================
# PAGE LAYOUT
# ============================================================

layout = html.Div(
    [
        # ====================================================
        # PAGE INTRO
        # ====================================================

        html.H1(
            "Skeletal Muscle Overview",
            style={
                "marginTop": 0,
            },
        ),

        html.P(
            "Study composition and participant characteristics "
            "across the discovery and validation cohorts.",
            style={
                "marginBottom": "26px",
            },
        ),


        # ====================================================
        # COHORT COMPOSITION
        # ====================================================

        html.Div(
            [
                html.H3(
                    "Cohort composition",
                    style={
                        "marginTop": 0,
                        "marginBottom": "3px",
                    },
                ),

                html.P(
                    "Participants by study cohort and PAD group.",
                    style={
                        "marginTop": 0,
                        "marginBottom": "12px",
                    },
                ),

                dcc.Graph(
                    figure=composition_fig,

                    config={
                        "displaylogo": False,
                    },

                    style={
                        "width": "100%",
                    },
                ),
            ],

            style={
                "border":
                    "1px solid var(--lab-border)",

                "borderRadius":
                    "8px",

                "padding":
                    "18px",

                # About 2/3 of previous width
                "width":
                    "100%",

                "maxWidth":
                    "1050px",

                "boxSizing":
                    "border-box",

                "marginBottom":
                    "28px",
            },
        ),


        # ====================================================
        # PARTICIPANT CHARACTERISTICS
        # ====================================================

        html.Div(
            [
                html.H3(
                    "Participant characteristics",
                    style={
                        "marginTop": 0,
                        "marginBottom": "3px",
                    },
                ),

                html.P(
                    "Summary characteristics by PAD group. "
                    "Continuous variables are shown as median "
                    "(IQR) and categorical variables as n (%).",
                    style={
                        "marginTop": 0,
                        "marginBottom": "18px",
                    },
                ),


                # ============================================
                # COHORT SELECTOR
                # ============================================

                html.Div(
                    [
                        html.Label(
                            "Cohort",
                            style={
                                "fontWeight": "700",
                                "fontSize": "13px",
                                "display": "block",
                                "marginBottom": "5px",
                            },
                        ),

                        dcc.Dropdown(
                            id="overview-table-cohort",

                            options=[
                                {
                                    "label":
                                        cohort,

                                    "value":
                                        cohort,
                                }
                                for cohort
                                in COHORT_ORDER
                            ],

                            value="Discovery",

                            clearable=False,
                        ),
                    ],

                    style={
                        "width": "230px",
                        "marginBottom": "18px",
                    },
                ),


                # ============================================
                # TABLE TITLE
                # ============================================

                html.Div(
                    id="overview-table-title",
                ),


                # ============================================
                # TABLE
                # ============================================

                html.Div(
                    id="overview-table-container",
                ),


                # ============================================
                # FOOTNOTES
                # ============================================

                html.Div(
                    [
                        html.P(
                            [
                                html.Strong(
                                    "Continuous variables: "
                                ),

                                "median (Q1–Q3). ",
                                
                                html.Strong(
                                    "Categorical variables: "
                                ),

                                "n (%). Percentages are based on "
                                "participants with non-missing data "
                                "for that variable.",
                            ],

                            style={
                                "marginTop": "16px",
                                "marginBottom": "5px",
                                "fontSize": "12px",
                                "color": "var(--lab-muted)",
                            },
                        ),

                        html.P(
                            [
                                html.Strong(
                                    "Statistical testing: "
                                ),

                                "Kruskal–Wallis for continuous "
                                "variables across three groups; "
                                "Mann–Whitney U when only two groups "
                                "were available. Categorical variables "
                                "used Pearson χ², Fisher exact, or "
                                "permutation χ² as appropriate. "
                                "FDR values use Benjamini–Hochberg "
                                "correction within each cohort.",
                            ],

                            style={
                                "marginTop": "0px",
                                "marginBottom": "0px",
                                "fontSize": "12px",
                                "color": "var(--lab-muted)",
                            },
                        ),
                    ],
                ),
            ],

            style={
                "border":
                    "1px solid var(--lab-border)",

                "borderRadius":
                    "8px",

                "padding":
                    "18px",

                "width":
                    "100%",

                "maxWidth":
                    "1050px",

                "boxSizing":
                    "border-box",

                "marginBottom":
                    "30px",
            },
        ),
    ]
)


# ============================================================
# TABLE CALLBACK
# ============================================================

@callback(
    Output(
        "overview-table-title",
        "children",
    ),

    Output(
        "overview-table-container",
        "children",
    ),

    Input(
        "overview-table-cohort",
        "value",
    ),
)
def update_overview_table(
    cohort,
):

    # ========================================================
    # NO TABLE YET
    # ========================================================

    if table1.empty:

        return (
            "",
            html.Div(
                [
                    html.Strong(
                        "Summary table not found."
                    ),

                    html.Div(
                        (
                            "Run the Table 1 generation script first "
                            "to create "
                            "Parquet/overview_table1.parquet."
                        ),
                        style={
                            "marginTop": "5px",
                        },
                    ),
                ],

                style={
                    "padding": "15px",
                    "color": "var(--lab-muted)",
                },
            ),
        )


    # ========================================================
    # FILTER COHORT
    # ========================================================

    data = (
        table1[
            table1["cohort"]
            == cohort
        ]
        .copy()
    )


    if data.empty:

        return (
            "",
            html.Div(
                "No summary data are available for this cohort.",
                style={
                    "padding": "15px",
                    "color": "var(--lab-muted)",
                },
            ),
        )


    # ========================================================
    # SORT
    # ========================================================

    sort_columns = []


    if (
        "variable_order"
        in data.columns
    ):

        sort_columns.append(
            "variable_order"
        )


    if (
        "level_order"
        in data.columns
    ):

        sort_columns.append(
            "level_order"
        )


    if sort_columns:

        data = (
            data
            .sort_values(
                sort_columns
            )
            .reset_index(
                drop=True
            )
        )


    # ========================================================
    # CLEAN DISPLAY VALUES
    # ========================================================

    data[
        "Variable"
    ] = (
        data[
            "display_label"
        ]
    )


    data[
        "HC_display"
    ] = (
        data[
            "HC"
        ]
        .fillna("—")
    )


    data[
        "SII_display"
    ] = (
        data[
            "S-II"
        ]
        .fillna("—")
    )


    data[
        "SIV_display"
    ] = (
        data[
            "S-IV"
        ]
        .fillna("—")
    )


    data[
        "P"
    ] = (
        data[
            "p_display"
        ]
        .fillna("—")
    )


    data[
        "FDR"
    ] = (
        data[
            "fdr_display"
        ]
        .fillna("—")
    )


    data[
        "Test"
    ] = (
        data[
            "test"
        ]
        .fillna("—")
    )


    # ========================================================
    # SHOW P/FDR/TEST ONLY ON FIRST ROW OF EACH VARIABLE
    # ========================================================
    #
    # This avoids repeating the exact same statistical
    # test for every level of categorical variables.
    # ========================================================

    first_variable_row = (
        ~data[
            "variable"
        ]
        .duplicated()
    )


    data.loc[
        ~first_variable_row,
        [
            "P",
            "FDR",
            "Test",
        ],
    ] = ""


    # ========================================================
    # KEEP SIGNIFICANCE FLAG
    # ========================================================

    data[
        "significant_display"
    ] = (
        data[
            "significant"
        ]
        .fillna(False)
        .astype(bool)
    )


    # ========================================================
    # GROUP Ns
    # ========================================================

    hc_header = make_group_header(
        cohort,
        "HC",
    )


    sii_header = make_group_header(
        cohort,
        "S-II",
    )


    siv_header = make_group_header(
        cohort,
        "S-IV",
    )


    # ========================================================
    # DATA FOR DASH
    # ========================================================

    table_data = (
        data[
            [
                "Variable",
                "HC_display",
                "SII_display",
                "SIV_display",
                "P",
                "FDR",
                "Test",
                "significant_display",
            ]
        ]
        .to_dict(
            "records"
        )
    )


    # ========================================================
    # TITLE
    # ========================================================

    title = html.H4(
        cohort,

        style={
            "marginTop": "2px",
            "marginBottom": "10px",
            "fontSize": "16px",
        },
    )


    # ========================================================
    # TABLE
    # ========================================================

    table = dash_table.DataTable(
        columns=[
            {
                "name":
                    "Variable",

                "id":
                    "Variable",
            },

            {
                "name":
                    hc_header,

                "id":
                    "HC_display",
            },

            {
                "name":
                    sii_header,

                "id":
                    "SII_display",
            },

            {
                "name":
                    siv_header,

                "id":
                    "SIV_display",
            },

            {
                "name":
                    "P",

                "id":
                    "P",
            },

            {
                "name":
                    "FDR",

                "id":
                    "FDR",
            },

            {
                "name":
                    "Test",

                "id":
                    "Test",
            },
        ],

        data=table_data,

        page_action="none",

        style_table={
            "overflowX":
                "auto",

            "width":
                "100%",
        },

        style_header={
            "backgroundColor":
                "#F5F8FA",

            "fontWeight":
                "700",

            "fontSize":
                "13px",

            "color":
                "var(--lab-navy-dark)",

            "textAlign":
                "left",

            "borderTop":
                "none",

            "borderLeft":
                "none",

            "borderRight":
                "none",

            "borderBottom":
                "2px solid var(--lab-border)",

            "padding":
                "9px 8px",
        },

        style_cell={
            "fontFamily":
                "Arial, sans-serif",

            "fontSize":
                "13px",

            "color":
                "var(--lab-navy-dark)",

            "textAlign":
                "left",

            "padding":
                "8px",

            "whiteSpace":
                "normal",

            "height":
                "auto",

            "borderTop":
                "none",

            "borderLeft":
                "none",

            "borderRight":
                "none",

            "borderBottom":
                "1px solid #E8EDF1",
        },

        style_cell_conditional=[
            {
                "if": {
                    "column_id":
                        "Variable",
                },

                "width":
                    "29%",

                "minWidth":
                    "220px",

                "fontWeight":
                    "600",
            },

            {
                "if": {
                    "column_id":
                        "HC_display",
                },

                "width":
                    "13%",
            },

            {
                "if": {
                    "column_id":
                        "SII_display",
                },

                "width":
                    "13%",
            },

            {
                "if": {
                    "column_id":
                        "SIV_display",
                },

                "width":
                    "13%",
            },

            {
                "if": {
                    "column_id":
                        "P",
                },

                "width":
                    "8%",
            },

            {
                "if": {
                    "column_id":
                        "FDR",
                },

                "width":
                    "8%",
            },

            {
                "if": {
                    "column_id":
                        "Test",
                },

                "width":
                    "16%",

                "fontSize":
                    "12px",

                "color":
                    "var(--lab-muted)",
            },
        ],

        style_data_conditional=[
            # --------------------------------------------
            # Significant FDR
            # --------------------------------------------

            {
                "if": {
                    "filter_query":
                        "{significant_display} = true",

                    "column_id":
                        "FDR",
                },

                "fontWeight":
                    "700",

                "color":
                    "#A50000",
            },

            # --------------------------------------------
            # Alternate very light rows
            # --------------------------------------------

            {
                "if": {
                    "row_index":
                        "odd",
                },

                "backgroundColor":
                    "#FBFCFD",
            },
        ],

        tooltip_header={
            "P":
                "Unadjusted P value",

            "FDR":
                "Benjamini–Hochberg adjusted P value",

            "Test":
                "Statistical test used for the overall comparison",
        },

        tooltip_delay=0,

        tooltip_duration=None,
    )


    return (
        title,
        table,
    )