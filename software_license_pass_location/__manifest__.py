{
    "name": "Software License (pass) Location",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "base_location",
        "software_license_pass",
    ],
    "data": [
        "views/software_license_pass.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "software_license_pass_location/static/src/css/style.scss",
        ],
    },
    "installable": True,
}
