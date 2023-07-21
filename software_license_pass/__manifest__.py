{
    "name": "Software License (pass)",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "software_license_token",
        "software_license_feature",
        "auth_signup_delegate",
        "sequence_reset_period",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/software_license_pass.xml",
        "views/software_license.xml",
        "views/software_license_pack.xml",
        "views/software_license_pack_line.xml",
        "views/menu.xml",
        "data/sequence.xml",
        "data/mail_template.xml",
        "data/uom.xml",
    ],
    "installable": True,
}
