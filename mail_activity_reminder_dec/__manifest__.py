{
    "name": "Mail Activity Reminder",
    "version": "18.0.1.0.0",
    "author": "DEC",
    "category": "Social Network",
    "website": "https://decgroupe.com",
    "license": "AGPL-3",
    "depends": [
        # "base_controller_user",  # optional
        "mail_activity_board",
        "mail_qweb",
        "mail_activity_team",
        "web_public_images",
    ],
    "data": [
        "data/ir_ui_view.xml",
        "data/mail_template.xml",
        "views/res_users.xml",
    ],
    "installable": True,
}
