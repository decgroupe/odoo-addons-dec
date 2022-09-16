{
    'name': 'Manufacturing (BoM supplier)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Add extra fields on BoM''',
    'depends':
        [
            'mrp',
            'product_legacy_routes',  # Needed for `supply_method` depends
        ],
    #'force_migration':'12.0.0.0.0',
    'data': ['views/mrp_bom.xml', ],
    'installable': True
}
