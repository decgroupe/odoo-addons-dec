{
    "name": "Manufacturing Timesheet",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "mrp_project",
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
    "installable": True,
}
