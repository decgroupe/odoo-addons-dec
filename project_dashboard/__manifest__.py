{
    'name': 'Project Dashboard',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Configure types to be displayed in a dashboard",
    'depends': [
        'project_category',
        'project_task_count',
        'mrp_project',
        'sale_timesheet_project',
    ],
    'data':
        [
            'views/project_project.xml',
            'views/project_type.xml',
            'views/menu.xml',
        ],
    'installable': True
}
