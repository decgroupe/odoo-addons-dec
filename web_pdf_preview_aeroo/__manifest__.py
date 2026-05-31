{
    "name": "Web PDF preview (Aeroo Support)",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "web_pdf_preview",
        "report_aeroo",
    ],
    "assets": {
        "web.assets_backend": [
            "web_pdf_preview_aeroo/static/src/js/report_preview_handler.esm.js",
        ],
    },
    "installable": True,
}
