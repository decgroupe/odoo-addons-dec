{
    "name": "Merge Projects",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "project",
        "project_type",  # needed by e-mail templates for merge notification
        "base_merge",
        "mail_qweb",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "wizard/merge_project.xml",
        "wizard/merge_task.xml",
        "data/ir_ui_view.xml",
        "data/mail_template_project.xml",
        "data/mail_template_task.xml",
    ],
    "installable": True,
}
