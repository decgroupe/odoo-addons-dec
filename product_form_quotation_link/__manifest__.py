{
    'name':
        'Product Form Quotation Link',
    'version':
        '12.0.1.0.0',
    'author':
        'DEC, Yann Papouin, ACSONE SA/NV,Odoo Community Association (OCA)',
    'website':
        'http://www.dec-industrie.com',
    'summary':
        '''Add an option to display the draft purchases lines from product''',
    'depends': [
        'purchase',
        'base_fontawesome',
    ],
    'data':
        [
            'views/purchase_order_line.xml',
            'views/product_template.xml',
            'views/product_product.xml',
        ],
    'installable':
        True
}