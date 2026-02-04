{
    "name": "Sale Timesheet Project",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "category": "Sales",
    "depends": [
        "project_identification",
        "sale_project",
        "sale_timesheet",
        "sale_delivery_last_date",
        "sale_action_view",
        "base_fontawesome",  # for project `fa-stopwatch` icon
    ],
    "data": [
        "views/sale_order.xml",
        "views/project_project.xml",
        "views/project_task.xml",
    ],
    "installable": True,
}
