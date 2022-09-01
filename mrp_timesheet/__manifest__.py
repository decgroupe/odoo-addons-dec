{
    'name': 'Manufacturing Timesheet',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Add HR Timesheet to the production orders for "
        "Production time tracking",
    'depends': [
        'mrp_project',
        'mrp_partner',
        'mrp_identification',
        'mrp_stage',
        'hr_timesheet',
    ],
    'data': [
        'views/mrp_production.xml',
        'views/hr_timesheet.xml',
        'views/project_task.xml',
    ],
    'installable': True
}
