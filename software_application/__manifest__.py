{
    "name": "Software Application",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "base_default",
        "mail",
        "product",
        "software",
    ],
    "external_dependencies": {
        "python": ["semver"],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/software_tag.xml",
        "views/software_application.xml",
        "views/software_application_release.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/product_product.xml",
        "demo/software_tag.xml",
        "demo/software_application.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "software_application/static/src/scss/style.scss",
        ],
    },
    "installable": True,  # TODO: rename images fields
}
