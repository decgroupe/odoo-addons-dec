{
    'name': 'Manufacturing (sale)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Get partner id from sale order shipping informations",
    'depends': [
        'mrp_partner',
        'mrp_stage',
        'sale_stock',
        'sale_mrp_link',
    ],
    'data': [
        'views/mrp_production.xml',
    ],
    'installable': True
}
