{
    'name': 'Manufacturing Partner Academy',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Add partner academy to production orders''',
    'depends': [
        'mrp_partner',
        'partner_academy',
    ],
    'data': ['views/mrp_production.xml', ],
    'installable': True
}
