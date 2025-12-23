{
    "name": "Project Identification",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "project_type",  # was "project_category"
    ],
    "data": [
        "data/project_type.xml",
        "views/project_project.xml",
        "views/project_task.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
