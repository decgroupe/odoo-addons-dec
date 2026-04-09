{
    "name": "Web Widget Markdown",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "web",
        "web_editor",  # to use `add_data` from controller
    ],
    "assets": {
        "web.assets_backend": [
            "web_widget_markdown/static/src/css/web_widget_markdown.scss",
            "web_widget_markdown/static/src/xml/web_widget_markdown.xml",
            "web_widget_markdown/static/src/js/web_widget_markdown.esm.js",
        ],
    },
    "demo": [
        "demo/markdown.xml",
    ],
    "installable": True,
}
