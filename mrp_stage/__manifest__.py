{
    "name": "Manufacturing Stages",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "mrp",
        "web_ir_actions_act_multi",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_activity_type.xml",
        "data/mrp_production_stage.xml",
        "views/mrp_production.xml",
        "views/mail_activity_type.xml",
        "views/mrp_production_stage.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mrp_stage/static/src/scss/kanban_view.scss",
        ],
    },
    "installable": True,
    "post_init_hook": "post_init_hook",
}
