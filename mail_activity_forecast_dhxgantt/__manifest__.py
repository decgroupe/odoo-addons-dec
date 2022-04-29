{
    'name': 'Mail Activity Forecast (Gantt)',
    'summary': "Forecast",
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'category': 'Social Network',
    'website': 'https://github.com/OCA/social',
    'license': 'AGPL-3',
    'depends':
        [
            'mail_activity_forecast',
            'mail_activity_partner',
            'mail_activity_project',
            'web_dhxgantt',
        ],
    "data": [
        'views/assets.xml',
        'views/mail_activity.xml',
    ],
    'qweb': ['static/src/xml/mail_activity_gantt_template.xml', ],
    'installable': True,
    # 'force_post_init_hook': True,
    # 'post_init_hook': 'post_init_hook',
}
