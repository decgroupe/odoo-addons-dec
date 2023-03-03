{
    'name': 'Manufacturing Swap Production',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        'Swap two manufacturing orders. This case can happen when you need '
        'to set an higher priority to a specific order.',
    'depends': [
        'mrp_timesheet',
        'sale_mrp_production_request_link',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'security/security.xml',
            'wizard/mrp_swap_production.xml',
            'wizard/mrp_swap_production_line.xml',
        ],
    'installable': True
}
