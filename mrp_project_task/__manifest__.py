{
    'name': 'Manufacturing Project Task',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Service production tracking",
    'depends':
        [
            'mrp_project',
            'mrp_purchase',
            'mrp_stage',
            'sale_timesheet',
            'sale_timesheet_task_exclude',
            'project_action_view',
            'project_identification',
        ],
    'data': [
        'views/mrp_production.xml',
        'views/project_task.xml',
    ],
    'installable': True
}