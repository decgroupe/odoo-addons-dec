{
    "name": "Software License",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "software_application",
        "base_fontawesome",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/software_license.xml",
        "views/software_application.xml",
        "views/software_license_hardware.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/software_license.xml",
        "demo/software_application.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "software_license/static/src/css/style.scss",
        ],
    },
    "installable": True,
}
