{
    "name": "Web Calendar Options",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "web",
        "calendar",
    ],
    "assets": {
        "web.assets_backend": [
            "web_calendar_options/static/src/scss/web_calendar.scss",
            "web_calendar_options/static/src/xml/web_calendar.xml",
            "web_calendar_options/static/src/js/calendar_renderer.esm.js",
            "web_calendar_options/static/src/js/calendar_controller.esm.js",
        ],
    },
    "installable": True,
}
