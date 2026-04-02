{
    "name": "Software License (legacy)",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "software_license_feature",
        "software_license_dongle",
    ],
    "data": [
        "data/software_license_feature.xml",
        "views/software_license.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
