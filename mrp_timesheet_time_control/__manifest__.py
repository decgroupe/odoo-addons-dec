{
    'name': 'Manufacturing Timesheet Time Control',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        "Exact start time for a timesheet line",
    'depends': [
        'mrp_timesheet',
        'project_timesheet_time_control',
    ],
    'data': [
        'views/mrp_production.xml',

    ],
    'installable': True
}
