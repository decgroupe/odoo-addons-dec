{
    'name': 'Mail Activity Forecast',
    'summary': "Forecast",
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'category': 'Social Network',
    'website': 'https://github.com/OCA/social',
    'license': 'AGPL-3',
    'depends': [
        'mail_activity_board',  # `calendar` is a hard dependency
    ],
    "data":
        [
            'data/mail_activity_type.xml',
            'views/mail_activity.xml',
            'views/mail_activity_type.xml',
        ],
    'qweb': [],
    'installable': True
}
