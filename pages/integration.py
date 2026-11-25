import dash

from dash import (
    html,
    dcc,
    Input,
    Output,
    callback,
    dash_table,
)

from pad_atlas_public.utils.loaders import load_table


dash.register_page(
    __name__,
    path="/integration",
    name="mRNA-miRNA Integration",
)


# ==================================================
# LOAD DATA
# ==================================================

integration = load_table(
    "mrna_mirna_integration"
)

integration_pathways = load_table(
    "integration_pathways"
)

membership = load_table(
    "module_membership"
)


# ==================================================
# HELPERS
# ==================================================

def module_sort_key(value):

    try:
        prefix, number = value.rsplit("-", 1)
        return prefix, int(number)

    except Exception:
        return value, 999


def format_p(value):

    if value is None:
        return "NS"

    try:
        if value != value:
            return "NS"
    except Exception:
        pass

    if value < 0.001:
        return f"{value:.2e}"

    return f"{value:.4f}"


def card(
    value,
    label,
):

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
            "minWidth": "160px",
        },
    )


# ==================================================
# MODULE LISTS
# ==================================================

mirna_modules = sorted(
    membership.loc[
        membership["feature_type"] == "mirna",
        "module_id",
    ]
    .dropna()
    .drop_duplicates()
    .tolist(),
    key=module_sort_key,
)


mrna_modules = sorted(
    membership.loc[
        membership["feature_type"] == "mrna",
        "module_id",
    ]
    .dropna()
    .drop_duplicates()
    .tolist(),
    key=module_sort_key,
)


# Fallbacks
if not mirna_modules:

    mirna_modules = [
        "miRNA-0",
        "miRNA-1",
        "miRNA-2",
    ]


if not mrna_modules:

    mrna_modules = [
        "mRNA-0",
        "mRNA-1",
        "mRNA-2",
        "mRNA-3",
        "mRNA-4",
    ]


# ==================================================
# DEFAULT MODULE PAIR
# ==================================================

if not integration.empty:

    valid_default = integration.dropna(
        subset=[
            "mirna_module_id",
            "mrna_module_id",
        ]
    ).copy()

    if not valid_default.empty:

        valid_default = (
            valid_default
            .sort_values(
                "fdr",
                na_position="last",
            )
        )

        default_row = (
            valid_default.iloc[0]
        )

        default_mirna_module = (
            "miRNA-0"
        )

        default_mrna_module = (
            "mRNA-0"
        )

    else:

        default_mirna_module = (
            "miRNA-0"
        )

        default_mrna_module = (
            "mRNA-0"
        )

else:

    default_mirna_module = (
        mirna_modules[0]
    )

    default_mrna_module = (
        mrna_modules[0]
    )


# ==================================================
# PAGE
# ==================================================

layout = html.Div(
    [
        # ==================================================
        # PAGE TITLE
        # ==================================================

        html.H1(
            "mRNA-miRNA Integration",
            style={
                "marginTop": 0,
            },
        ),

        html.P(
            "Explore module-level relationships between "
            "skeletal muscle miRNA and mRNA co-expression networks."
        ),


        # ==================================================
        # STATIC NETWORK SVG
        # ==================================================

        html.Div(
            [
                html.H3(
                    "Direct module integration",

                    style={
                        "marginTop": 0,
                        "marginBottom": "5px",
                    },
                ),

                html.P(
                    "Module-level integration between miRNA and mRNA "
                    "co-expression networks. Darker connections indicate "
                    "significant relationships, while lighter connections "
                    "represent non-significant relationships.",

                    style={
                        "marginTop": 0,
                        "marginBottom": "15px",
                    },
                ),

                html.Img(
                    src="/assets/miRNA-mRNA.svg",

                    alt=(
                        "miRNA-mRNA module integration network"
                    ),

                    style={
                        "display": "block",
                        "width": "100%",
                        "maxWidth": "900px",
                        "height": "auto",
                        "margin": "0",
                    },
                ),
            ],

            style={
                "border": "1px solid #ddd",
                "borderRadius": "8px",
                "padding": "20px",
                "maxWidth": "950px",
                "marginBottom": "30px",
                "boxSizing": "border-box",
                "backgroundColor": "white",
            },
        ),


        # ==================================================
        # MODULE PAIR EXPLORER
        # ==================================================

        html.H2(
            "Module pair explorer",

            style={
                "marginBottom": "6px",
            },
        ),

        html.P(
            "Select a miRNA and mRNA module pair to inspect "
            "the direct integration result and shared "
            "KEGG pathways."
        ),


        # --------------------------------------------------
        # CONTROLS
        # --------------------------------------------------

        html.Div(
            [
                # miRNA module
                html.Div(
                    [
                        html.Label(
                            "miRNA module",

                            style={
                                "fontWeight": "bold",
                                "fontSize": "13px",
                            },
                        ),

                        dcc.Dropdown(
                            id=(
                                "integration-"
                                "mirna-module"
                            ),

                            options=[
                                {
                                    "label": x,
                                    "value": x,
                                }
                                for x
                                in mirna_modules
                            ],

                            value=(
                                default_mirna_module
                            ),

                            clearable=False,
                        ),
                    ],

                    style={
                        "width": "250px",
                    },
                ),


                # mRNA module
                html.Div(
                    [
                        html.Label(
                            "mRNA module",

                            style={
                                "fontWeight": "bold",
                                "fontSize": "13px",
                            },
                        ),

                        dcc.Dropdown(
                            id=(
                                "integration-"
                                "mrna-module"
                            ),

                            options=[
                                {
                                    "label": x,
                                    "value": x,
                                }
                                for x
                                in mrna_modules
                            ],

                            value=(
                                default_mrna_module
                            ),

                            clearable=False,
                        ),
                    ],

                    style={
                        "width": "250px",
                    },
                ),
            ],

            style={
                "display": "flex",
                "gap": "20px",
                "flexWrap": "wrap",
                "marginBottom": "24px",
            },
        ),


        # --------------------------------------------------
        # DYNAMIC OUTPUT
        # --------------------------------------------------

        html.Div(
            id="integration-pair-content",
        ),
    ]
)


# ==================================================
# MODULE PAIR CALLBACK
# ==================================================

@callback(
    Output(
        "integration-pair-content",
        "children",
    ),

    Input(
        "integration-mirna-module",
        "value",
    ),

    Input(
        "integration-mrna-module",
        "value",
    ),
)
def update_module_pair(
    mirna_module,
    mrna_module,
):

    # ==================================================
    # DIRECT MODULE INTEGRATION
    # ==================================================

    direct = integration[
        (
            integration[
                "mirna_module_id"
            ]
            == mirna_module
        )
        &
        (
            integration[
                "mrna_module_id"
            ]
            == mrna_module
        )
    ]


    if direct.empty:

        direct_p = "NS"
        direct_fdr = "NS"
        direct_sig = "No direct result"

    else:

        direct_row = (
            direct.iloc[0]
        )


        direct_p = format_p(
            direct_row[
                "p_value"
            ]
        )


        direct_fdr = format_p(
            direct_row[
                "fdr"
            ]
        )


        raw_fdr = (
            direct_row[
                "fdr"
            ]
        )


        if (
            raw_fdr is not None
            and raw_fdr == raw_fdr
            and raw_fdr < 0.05
        ):

            direct_sig = "Yes"

        else:

            direct_sig = "No"


    # ==================================================
    # SHARED KEGG PATHWAYS
    # ==================================================

    pathway_rows = integration_pathways[
        (
            integration_pathways[
                "mirna_module_id"
            ]
            == mirna_module
        )
        &
        (
            integration_pathways[
                "mrna_module_id"
            ]
            == mrna_module
        )
        &
        (
            integration_pathways[
                "database"
            ]
            == "KEGG"
        )
    ].copy()


    pathway_rows = (
        pathway_rows
        .sort_values(
            [
                "fdr",
                "p_value",
            ],

            na_position="last",
        )
    )


    n_shared = len(
        pathway_rows
    )


    n_significant = int(
        (
            pathway_rows[
                "fdr"
            ].notna()
            &
            (
                pathway_rows[
                    "fdr"
                ]
                < 0.05
            )
        )
        .sum()
    )


    # ==================================================
    # PATHWAY TABLE
    # ==================================================

    table_data = []


    for _, pathway_row in (
        pathway_rows
        .head(50)
        .iterrows()
    ):

        pathway_fdr = (
            pathway_row[
                "fdr"
            ]
        )


        pathway_sig = (
            "Yes"

            if (
                pathway_fdr
                is not None

                and pathway_fdr
                == pathway_fdr

                and pathway_fdr
                < 0.05
            )

            else "No"
        )


        table_data.append(
            {
                "pathway_name":
                    pathway_row[
                        "pathway_name"
                    ],

                "p_value":
                    format_p(
                        pathway_row[
                            "p_value"
                        ]
                    ),

                "fdr":
                    format_p(
                        pathway_row[
                            "fdr"
                        ]
                    ),

                "significant":
                    pathway_sig,
            }
        )


    # ==================================================
    # OUTPUT
    # ==================================================

    return html.Div(
        [
            # --------------------------------------------------
            # Selected pair
            # --------------------------------------------------

            html.H3(
                (
                    f"{mirna_module} → "
                    f"{mrna_module}"
                ),

                style={
                    "marginBottom": "12px",
                },
            ),


            # --------------------------------------------------
            # SUMMARY CARDS
            # --------------------------------------------------

            html.Div(
                [
                    card(
                        direct_sig,
                        "Direct integration",
                    ),
                    
                    card(
                        direct_p,
                        "Direct P value",
                    ),

                    card(
                        direct_fdr,
                        "Direct FDR",
                    ),



                    card(
                        n_shared,
                        "Shared KEGG pathways",
                    ),

                    card(
                        n_significant,
                        "Significant KEGG pathways",
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
            # SHARED KEGG PATHWAYS
            # --------------------------------------------------

            html.Div(
                [
                    html.H3(
                        "Shared KEGG pathways",

                        style={
                            "marginTop": 0,
                            "marginBottom": "5px",
                        },
                    ),

                    html.P(
                        "KEGG pathways shared between "
                        "the selected miRNA and mRNA modules.",

                        style={
                            "marginTop": 0,
                            "marginBottom": "12px",
                        },
                    ),


                    (
                        dash_table.DataTable(
                            columns=[
                                {
                                    "name": "Pathway",
                                    "id": "pathway_name",
                                },

                                #{
                                #    "name": "P value",
                                #    "id": "p_value",
                                #},

                                #{
                                #    "name": "FDR",
                                #    "id": "fdr",
                                #},

                                #{
                                #    "name": "Significant",
                                #    "id": "significant",
                                #},
                            ],

                            data=table_data,

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
                            },

                            style_cell_conditional=[
                                {
                                    "if": {
                                        "column_id":
                                            "pathway_name"
                                    },

                                    "minWidth":
                                        "300px",

                                    "maxWidth":
                                        "500px",
                                },
                            ],
                        )

                        if table_data

                        else html.Div(
                            (
                                "No shared KEGG pathways "
                                "were found for this "
                                "module pair."
                            ),

                            style={
                                "padding": "18px 0",
                                "color": "#607483",
                            },
                        )
                    ),
                ],

                style={
                    "border": "1px solid #ddd",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "maxWidth": "950px",
                    "boxSizing": "border-box",
                },
            ),


            # --------------------------------------------------
            # INTERPRETATION NOTE
            # --------------------------------------------------

            html.P(
                "Integration shown here is module-level. "
                "It should not be interpreted as direct "
                "miRNA-gene regulatory interactions.",

                style={
                    "fontSize": "13px",
                    "color": "#607483",
                    "marginTop": "14px",
                    "maxWidth": "950px",
                },
            ),
        ]
    )