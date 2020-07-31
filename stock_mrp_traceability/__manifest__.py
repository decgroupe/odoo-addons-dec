{
    'name': 'Stock Manufacturing Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Show picking line origin''',
    'depends': [
        'stock',
        'mrp',
        # testing to remove
        'mrp_traceability',
    ],
    'data': ['views/stock_picking.xml', ],
    'installable': True
}
