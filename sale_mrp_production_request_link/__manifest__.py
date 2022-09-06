{
    'name': 'Sale Manufacturing Production Request Link',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Sales',
    'summary':
        "Show manufacturing production requests generated from sale "
        "orders and create activities when sale orders are cancelled",
    'depends':
        [
            'sale_mrp_link',
            'mrp_production_request',
            'mrp_production_request_action_view',
        ],
    'data':
        [
            'data/mail_template.xml',
            'views/sale_order.xml',
            'views/mrp_production_request.xml',
        ],
    'installable': True
}
