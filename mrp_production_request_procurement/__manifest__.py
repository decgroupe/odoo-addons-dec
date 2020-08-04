{
    'name': 'MRP Production Request Procurement',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Allow customization of the procurement group assigned to MO''',
    'depends': [
        'mrp',
        'mrp_production_request',
    ],
    'data': [
        'views/mrp_production.xml',
    ],
    'installable': True
}
