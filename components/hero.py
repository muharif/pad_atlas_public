from dash import html


def hero():

    return html.Div(
        [
            html.Div(
                [
                    html.H1(
                        "PAD Atlas",
                        className="hero-title",
                    ),

                    html.Div(
                        "A multi-omic atlas of peripheral artery disease.",
                        className="hero-subtitle",
                    ),

                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong("235"),
                                    " participants",
                                ],
                                className="hero-chip",
                            ),

                            html.Div(
                                [
                                    html.Strong("3"),
                                    " cohorts",
                                ],
                                className="hero-chip",
                            ),

                            html.Div(
                                "Multi-omics",
                                className="hero-chip",
                            ),

                            html.Div(
                                "Integrated analysis",
                                className="hero-chip",
                            ),
                        ],
                        className="hero-chips",
                    ),
                ],
                className="hero-content",
            ),
        ],
        className="hero",
    )