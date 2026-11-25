from dash import html, dcc


NAV_ITEMS = [
    ("Overview", "/"),
    ("Genes", "/genes"),
    ("Differential Expression", "/differential-expression"),
    ("Cross-cohort Validation", "/validation"),
    ("Pathways", "/pathways"),
    ("mRNA Networks", "/mrna-networks"),
    ("miRNA", "/mirna"),
    ("Integration", "/integration"),
    ("Senescence", "/senescence"),
    ("Clinical", "/clinical"),
]


def navbar():

    return html.Div(
        [
            dcc.Link(
                label,
                href=href,
                style={
                    "textDecoration": "none",
                    "color": "#222",
                    "fontSize": "14px",
                    "fontWeight": "500",
                    "padding": "9px 12px",
                    "borderRadius": "6px",
                    "whiteSpace": "nowrap",
                },
            )
            for label, href in NAV_ITEMS
        ],
        style={
            "display": "flex",
            "gap": "4px",
            "flexWrap": "wrap",
            "padding": "10px 28px",
            "borderBottom": "1px solid #ddd",
            "backgroundColor": "#fafafa",
        },
    )