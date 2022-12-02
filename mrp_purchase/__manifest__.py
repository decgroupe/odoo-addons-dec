{
    'name': 'Manufacturing Purchase',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Service purchase tracking",
    'depends': [
        'purchase_subcontracted_service',
        'mrp_production_service',
    ],
    'data': [
        'data/mail_activity_template.xml',
        'views/mrp_production.xml',
        'views/purchase_order.xml',
    ],
    'installable': True
}