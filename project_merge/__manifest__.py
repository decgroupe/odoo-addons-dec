{
    "name": "Merge Projects",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "project",
        "project_list", # needed otherwise the merge action is not visible
        "project_category", # needed by e-mail templates for merge notification
        "deltatech_merge",
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
