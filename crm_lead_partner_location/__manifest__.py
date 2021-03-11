{
    'name': 'CRM Partner Location',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Add partner location to CRM''',
    'depends': [
        'crm',
        'base_location',
    ],
    'data': ['views/crm_lead.xml', ],
    'installable': True
}
