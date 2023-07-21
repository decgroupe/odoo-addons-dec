{
    "name": "Software Application",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "base",
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
        "views/assets.xml",
    ],
    "installable": True,
}
