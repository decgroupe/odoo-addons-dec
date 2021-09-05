{
    'name': 'Stock Orderpoint Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Use existing orderpoint_id(s) from other models to link''',
    'depends':
        [
            'stock',
            'stock_traceability',
            'stock_orderpoint_mrp_link',
            'stock_orderpoint_purchase_link',
        ],
    'data': ['views/stock_picking.xml', ],
    'installable': True
}
