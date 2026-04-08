# Copyright 2017-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2017-2018 manawi <https://github.com/manawi>
# Copyright 2017 Karamov Ilmir <https://it-projects.info/team/ilmir-k>
# Copyright 2017-2018 iledarn <https://github.com/iledarn>
# Copyright 2018-2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2020 Almas Giniatullin <https://github.com/almas50>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": "Project Task Checklist",
    "category": "Project Management",
    "version": "18.0.1.0.0",
    "application": False,
    "author": "DEC, IT-Projects LLC, Manaev Rafael",
    "website": "https://decgroupe.com",
    "license": "AGPL-3",
    "depends": ["base", "project"],
    "data": [
        "security/ir.model.access.csv",
        "security/project_security.xml",
        "views/project_task_subtask.xml",
        "views/project_task.xml",
        "views/menu.xml",
        "data/subscription_template.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "project_task_subtask/static/src/scss/kanban_styles.scss",
        ],
    },
    "installable": True,
}
