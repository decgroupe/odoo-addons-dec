{
    "name": "Web From Ordered-By",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "category": "Base",
    "depends": [
        "web",
    ],
    "assets": {
        "web.assets_backend": [
            "web_form_orderedby/static/src/js/form_controller.esm.js",
        ],
        "web.assets_unit_tests": [
            "web_form_orderedby/static/tests/**/*",
        ],
    },
    "installable": True,
}
