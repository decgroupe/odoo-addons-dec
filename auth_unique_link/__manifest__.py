{
    "name": "Auth Unique Link",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "web",
        "mail_qweb",
        "portal",  # needed for unit testing only
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/ir_ui_view.xml",
        "data/mail_template.xml",
        "templates/login_templates.xml",
        "wizard/res_partner_impersonate.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "auth_unique_link/static/src/css/style.scss",
        ],
    },
    "installable": True,
}
