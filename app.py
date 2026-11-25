from dash import (
    Dash,
    html,
    page_container,
)

from pad_atlas_public.components.sidebar import sidebar
from pad_atlas_public.components.hero import hero


app = Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    suppress_callback_exceptions=True,
)


app.layout = html.Div(
    [
        # ==========================================
        # PERMANENT LEFT SIDEBAR
        # ==========================================

        sidebar(),

        # ==========================================
        # RIGHT SIDE
        # ==========================================

        html.Div(
            [
                # ----------------------------------
                # PERMANENT HERO
                # ----------------------------------

                hero(),

                # ----------------------------------
                # ONLY THIS PART CHANGES
                # ----------------------------------

                html.Main(
                    page_container,
                    className="page-content",
                ),
            ],
            className="main-content",
        ),
    ]
)


if __name__ == "__main__":

    app.run(
        debug=True,
        port=8050,
        host='0.0.0.0',
        dev_tools_hot_reload=False,
    )
