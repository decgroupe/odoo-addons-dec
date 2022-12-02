{
    'name': 'Partner Identification (base_location)',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Use base_location when customizing name search",
    'depends': [
        'partner_identification_base',
        'base_location',
    ],
    'data': [
        'views/partner_view.xml',
    ],
    'installable': True
}
