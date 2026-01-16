{
    "name": "Software License (token)",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "external_dependencies": {
        "python": [
            "Crypto",  # pip install pycryptodome
        ],
    },
    "depends": [
        "software_license_feature",
    ],
    "data": [
        "views/software_license.xml",
        "views/software_license_hardware.xml",
        "views/software_application.xml",
    ],
    "demo": [
        "demo/software_application.xml",
        "demo/software_license.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "software_license_token/static/src/css/style.scss",
        ],
    },
    "installable": True,
}
