# Copyright 2017-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2017-2018 manawi <https://github.com/manawi>
# Copyright 2017 Karamov Ilmir <https://it-projects.info/team/ilmir-k>
# Copyright 2017-2018 iledarn <https://github.com/iledarn>
# Copyright 2018-2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2020 Almas Giniatullin <https://github.com/almas50>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": "Project Task Checklist",
    "summary":
        "Use checklist to be ensure that all your tasks are "
        "performed and to make easy control over them",
    "category": "Project Management",
    "version": "14.0.1.0.0",
    "application": False,
    "author": "DEC, Yann Papouin, "
              "IT-Projects LLC, Manaev Rafael",
    'website': 'https://www.decgroupe.com',
    "license": "MIT",
    "depends": ["base", "project"],
    "external_dependencies": {
        "python": [],
        "bin": []
    },
    "data":
        [
            "security/ir.model.access.csv",
            "security/project_security.xml",
            "views/project_task_subtask.xml",
            "views/assets.xml",
            "data/subscription_template.xml",
        ],
    "qweb": ["static/src/xml/templates.xml"],
    "demo": ["demo/project_task_subtask_demo.xml"],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "auto_install": False,
    "installable": True,
}
