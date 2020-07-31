{
    'name': 'Stock Manufacturing Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Show picking line origin''',
    'depends': [
        'stock',
        'mrp',
        'mrp_production_request',
        'stock_traceability',
        'stock_orderpoint_traceability',
    ],
    'data': ['views/stock_picking.xml', ],
    'installable': True
}
