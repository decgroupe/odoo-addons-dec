{
    'name': 'Project Schedule',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Schedule",
    'depends': [
        'mail_activity_schedule',
        'project_activity',
    ],
    'data': [],
    'force_post_init_hook': True,
    'post_init_hook': 'post_init_hook',
    'installable': True
}