{
    'name': 'Project Partner Location',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Add shipping partner location from sale orders",
    'depends':
        [
            'project',
            'sale_timesheet_project',
            'sale_partner_location',
            'mrp_project_task',
            'mrp_partner_location',
            'partner_identification_base',
        ],
    'data': [
        'views/project_project.xml',
        'views/project_task.xml',
    ],
    'installable': True
}
