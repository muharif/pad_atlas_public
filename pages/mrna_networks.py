import dash
from dash import html, dcc, Input, Output, callback, dash_table
import plotly.express as px

from pad_atlas_public.utils.loaders import load_table


dash.register_page(
    __name__,
    path="/mrna-networks",
    name="mRNA Networks",
)


membership = load_table(
    "module_membership"
)

summary = load_table(
    "module_summary"
)


mrna_membership = membership[
    membership["feature_type"] == "mrna"
].copy()


MODULES = sorted(
    mrna_membership["module_id"]
    .dropna()
    .unique()
)


def card(value, label):

    return html.Div(
        [
            html.Div(
                str(value),
                style={
                    "fontSize": "25px",
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


def safe_value(
    row,
    column,
    default="—",
):

    if column not in row.index:
        return default

    value = row[column]

    if value != value:
        return default

    return value


layout = html.Div(
    [
        html.H1(
            "mRNA Networks",
            style={"marginTop": 0},
        ),

        html.P(
            "Explore mRNA co-expression modules and highly "
            "connected module genes."
        ),

        html.Div(
            [
                html.Label(
                    "mRNA module",
                    style={
                        "fontWeight": "bold",
                    },
                ),

                dcc.Dropdown(
                    id="mrna-module-selector",
                    options=[
                        {
                            "label": module,
                            "value": module,
                        }
                        for module in MODULES
                    ],
                    value=MODULES[0],
                    clearable=False,
                ),
            ],
            style={
                "width": "240px",
                "marginBottom": "28px",
            },
        ),

        html.Div(
            id="mrna-network-content"
        ),
    ]
)


@callback(
    Output(
        "mrna-network-content",
        "children",
    ),
    Input(
        "mrna-module-selector",
        "value",
    ),
)
def update_module(
    module_id,
):

    members = (
        mrna_membership[
            mrna_membership["module_id"]
            == module_id
        ]
        .sort_values(
            "degree",
            ascending=False,
        )
        .copy()
    )

    s = summary[
        summary["module_id"]
        == module_id
    ]

    if s.empty:

        n_features = len(members)
        mean_degree = members["degree"].mean()
        median_degree = members["degree"].median()
        max_degree = members["degree"].max()

        top_hub = (
            members.iloc[0]["feature_id"]
            if not members.empty
            else "—"
        )

        row = None

    else:

        row = s.iloc[0]

        n_features = int(
            safe_value(
                row,
                "n_features",
                len(members),
            )
        )

        mean_degree = safe_value(
            row,
            "mean_degree",
            members["degree"].mean(),
        )

        median_degree = safe_value(
            row,
            "median_degree",
            members["degree"].median(),
        )

        max_degree = safe_value(
            row,
            "max_degree",
            members["degree"].max(),
        )

        top_hub = safe_value(
            row,
            "top_hub_feature",
            members.iloc[0]["feature_id"],
        )

    top = (
        members
        .head(25)
        .sort_values("degree")
    )

    fig = px.bar(
        top,
        x="degree",
        y="feature_id",
        orientation="h",
        hover_data={
            "degree": True,
            "module_id": True,
        },
        labels={
            "degree": "Degree centrality",
            "feature_id": "",
        },
    )

    fig.update_layout(
        height=650,
        margin=dict(
            l=40,
            r=20,
            t=20,
            b=40,
        ),
        showlegend=False,
    )

    extra_cards = []

    if row is not None:

        for column, label in [
            (
                "ic_discovery_deg_n",
                "IC Discovery DEGs",
            ),
            (
                "cli_discovery_deg_n",
                "CLI Discovery DEGs",
            ),
            (
                "shared_progressive_n",
                "Shared progressive",
            ),
        ]:

            if column in row.index:

                value = safe_value(
                    row,
                    column,
                )

                if value != "—":
                    value = int(value)

                extra_cards.append(
                    card(
                        value,
                        label,
                    )
                )

    table_data = (
        members[
            [
                "feature_id",
                "degree",
            ]
        ]
        .head(50)
        .to_dict("records")
    )

    return html.Div(
        [
            html.Div(
                [
                    card(
                        n_features,
                        "Genes",
                    ),
                    card(
                        f"{mean_degree:.1f}",
                        "Mean degree",
                    ),
                    card(
                        f"{median_degree:.1f}",
                        "Median degree",
                    ),
                    card(
                        f"{max_degree:.0f}",
                        "Maximum degree",
                    ),
                    card(
                        top_hub,
                        "Top hub",
                    ),
                    *extra_cards,
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
                        f"{module_id} hubs",
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
                    "maxWidth": "900px",
                    "marginBottom": "20px",
                },
            ),

            html.Div(
                [
                    html.H3(
                        "Module genes",
                        style={"marginTop": 0},
                    ),

                    dash_table.DataTable(
                        columns=[
                            {
                                "name": "Gene",
                                "id": "feature_id",
                            },
                            {
                                "name": "Degree centrality",
                                "id": "degree",
                            },
                        ],
                        data=table_data,
                        sort_action="native",
                        page_size=20,
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
                    "maxWidth": "900px",
                },
            ),
        ]
    )