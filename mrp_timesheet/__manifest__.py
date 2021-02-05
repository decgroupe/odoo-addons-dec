{
    'name': 'Manufacturing Timesheet',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        "Add HR Timesheet to the production orders for "
        "Production time tracking",
    'depends': [
        'mrp_project',
        'mrp_partner',
    ],
    'data': [
        'views/mrp_production.xml',
        'views/hr_timesheet.xml',
    ],
    'installable': True
}
