{
    'name': 'Production Request Partner Info',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Add fields related to partner like city''',
    'depends': [
        'mrp_partner',
        'sale_mrp_production_request_link',
    ],
    'data': [
        'views/mrp_production_request.xml',
    ],
    'installable': True
}
