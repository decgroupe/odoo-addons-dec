{
    "name": "Manufacturing Timesheet",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "mrp_project_auto",
        "mrp_partner",
        "mrp_identification",
        "mrp_stage",
        "hr_timesheet",
        "hr_timesheet_autofill",
    ],
    "data": [
        "views/mrp_production.xml",
        "views/hr_timesheet.xml",
        "views/project_task.xml",
    ],
    "demo": [
        "demo/mrp_production.xml",
    ],
    "installable": True,
}
