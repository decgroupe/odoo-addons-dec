{
    "name": "Manufacturing Timesheet Distribution",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "mrp_timesheet_time_control",
        "mrp_project_task",
        "project_identification",
        "project_task_default_stage",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mrp_distribute_timesheet_reason.xml",
        "wizard/mrp_distribute_timesheet.xml",
    ],
    "installable": True,
}
