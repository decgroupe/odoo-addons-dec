{
    "name": "Software License (Portal)",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "portal",
        "software_license_token",
        "software_license_dongle",
        "software_license_pass",
        "partner_identification_base", # for emojis
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/software_license.xml",
        "views/software_application.xml",
        "templates/software_license.xml",
        "templates/software_license_pass.xml",
    ],
    "installable": True,
}
