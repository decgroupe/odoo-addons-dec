{
    'name': 'Purchase Subcontracted Service',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        "Override `subcontracted_service` behaviour in order to use the "
        "existing `service_to_purchase` field",
    'depends': [
        'subcontracted_service',
        'sale_purchase',
    ],
    'data': ['views/product_template.xml', ],
    'installable': True
}
