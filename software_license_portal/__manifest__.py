{
    "name": "Software License (Portal)",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "portal",
        "software_license_token",
        "software_license_dongle",
        "software_license_pass",
        "partner_identification_base",  # for symbols
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/software_license.xml",
        "views/software_application.xml",
        "templates/software_license.xml",
        "templates/software_license_pass.xml",
    ],
    "assets": {
        "web.assets_tests": [
            "software_license_portal/static/tests/tours/test_pass_tour.esm.js"
        ],
    },
    "installable": True,
}
