{
    "name": "Mail Activity Schedule (Gantt)",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "category": "Social Network",
    "website": "https://github.com/OCA/social",
    "license": "AGPL-3",
    "depends": [
        "mail_activity_schedule",
        "web_dhxgantt",
    ],
    "data": [
        "views/assets.xml",
        "views/mail_activity.xml",
    ],
    "qweb": [
        "static/src/xml/mail_activity_gantt_template.xml",
    ],
    "installable": True,
    # 'force_post_init_hook': True,
    # 'post_init_hook': 'post_init_hook',
}
