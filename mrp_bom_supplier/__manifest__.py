{
    'name': 'Manufacturing (BoM supplier)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Add extra fields on BoM''',
    'depends': [
        'mrp',
    ],
    #'force_migration':'12.0.0.0.0',
    'data': [
        'views/mrp_bom.xml',
    ],
    'installable': True
}
