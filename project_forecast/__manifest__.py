{
    'name': 'Project Forecast',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Forecast",
    'depends': [
        'mail_activity_forecast',
        'project_activity',
    ],
    'data': [],
    'force_post_init_hook': True,
    'post_init_hook': 'post_init_hook',
    'installable': True
}
