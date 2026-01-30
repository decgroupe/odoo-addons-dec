{
    "name": "Web Backend Theme",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "category": "Theme/Backend",
    "depends": [
        "web",
        "web_responsive",
        "mail",
        # check web_theme_classic, web_dark_mode
    ],
    "assets": {
        "web._assets_core": [
            "web_backend_theme/static/src/core/dialog/dialog.scss",
            "web_backend_theme/static/src/core/dropdown/dropdown.scss",
        ],
        "web._assets_primary_variables": [
            (
                "before",
                "web/static/src/scss/primary_variables.scss",
                "web_backend_theme/static/src/scss/primary_variables.scss",
            ),
        ],
        "web.assets_web": [
            "web_backend_theme/static/src/scss/web_theme_classic.scss",
            "web_backend_theme/static/src/chatter/web/chatter.xml",
            "web_backend_theme/static/src/webclient/navbar/navbar.xml",
        ],
        "web.assets_backend": [
            (
                "after",
                "web_responsive/static/src/legacy/scss/web_responsive.scss",
                "web_backend_theme/static/src/scss/web_responsive.scss",
            ),
            (
                "after",
                "web/static/src/webclient/navbar/navbar.scss",
                "web_backend_theme/static/src/webclient/navbar/navbar.scss",
            ),
            "web_backend_theme/static/src/webclient/loading_indicator/loading_indicator.scss",
            "web_backend_theme/static/src/views/list/list_renderer.scss",
            "web_backend_theme/static/src/views/form/form_controller.scss",
            "web_backend_theme/static/src/core/web/activity_menu.xml",
        ],
    },
    "installable": True,
    "application": True,
}
