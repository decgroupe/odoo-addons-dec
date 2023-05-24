{
    "name": "Manufacturing Stages",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "mrp",
        "web_kanban_draggable",
        "web_ir_actions_act_multi",
        "web_ir_actions_act_view_reload",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_activity_type.xml",
        "data/mrp_production_stage.xml",
        "views/assets.xml",
        "views/mrp_production.xml",
        "views/mail_activity_type.xml",
        "views/mrp_production_stage.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
