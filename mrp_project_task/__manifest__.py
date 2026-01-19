{
    "name": "Manufacturing Project Task",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "mrp_project",
        "mrp_purchase",  # because of _action_launch_procurement_rule
        "mrp_stage",
        "mrp_partner",
        "sale_timesheet",
        "sale_timesheet_line_exclude",
        # 'sale_timesheet_task_exclude', [MIG] 14.0: Not needed anymore acoording to https://github.com/OCA/timesheet/pull/440#issuecomment-1235611830
        "project_action_view",
        "project_identification",
        "project_task_stage_state",
    ],
    "data": [
        "views/mrp_production.xml",
        "views/project_task.xml",
        "data/mail_activity_template.xml",
    ],
    "installable": True,
}
