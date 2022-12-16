{
    'name': 'Project My Activities',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Backport next activity workflow from Odoo 14.0 but use current"
        "user",
    'depends':
        [
            'project',
            'project_activity',
            'project_user',
            'web_widget_mail_list_activity',
            'web',
            'mail_activity_my',
        ],
    'data': [
        'views/project_task.xml',
        'views/project_project.xml',
    ],
    'installable': True
}
