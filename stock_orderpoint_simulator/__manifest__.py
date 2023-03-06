{
    'name': 'Orderpoint Simulator',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Add wizard to help building a valid and wanted rule''',
    'depends': ['stock_orderpoint_auto_multiple'],
    'data':
        [
            'wizard/stock_warehouse_orderpoint_simulator.xml',
            'views/stock_warehouse_orderpoint.xml',
            'security/ir.model.access.csv',
        ],
    'installable': True
}
