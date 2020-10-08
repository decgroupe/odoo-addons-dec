{
    'name': 'Manufacturing (transtion)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Transition only (OpenERP to Odoo)''',
    'depends': [
        'mrp',
        'stock',
        'stock_mrp_traceability',
    ],
    'data': [
        'security/res_groups.xml',
        'views/mrp_production.xml',
    ],
    'installable': True
}
