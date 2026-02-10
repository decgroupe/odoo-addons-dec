{
    "name": "Project Dashboard",
    "version": "18.0.1.0.0",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "project_type",  # was "project_category"
        # "project_partner_location",
        "project_task_count", # for `todo_task_count`
        "mrp_project",  # for `todo_production_count`
    ],
    "data": [
        "views/project_project.xml",
        "views/project_type.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/project_type.xml",
        "demo/project_project.xml",
        "demo/project_task.xml",
        "demo/project_project_dates.xml",
    ],
    "installable": True,
}
