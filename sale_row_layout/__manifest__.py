{
    'name': 'Sale Row Layout',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Sales',
    'summary': "Show line form product fields using a row",
    'depends': [
        'product',
        'sale_margin',
        'sale_stock',
    ],
    #'force_migration':'12.0.0.0.0',
    'data':
        [
            'views/assets.xml',
            # FIXME: [MIG] 14.0: Disabled because issue with View name: sale.order.line.tree.sale.stock.qty
            'views/sale_order.xml', 
        ],
    'installable': True
}
