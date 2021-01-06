{
    'name': 'Manufacturing (timesheet)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Manually create workorders after/during production''',
    'depends': [
        'mrp',
        'mrp_workorder_sequence',
    ],
    'data': [
        'views/mrp_workorder.xml',
    ],
    'installable': True
}
