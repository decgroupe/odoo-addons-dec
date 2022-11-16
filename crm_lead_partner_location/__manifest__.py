{
    'name': 'CRM Partner Location',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Add partner shipping address and location to CRM",
    'depends': [
        'crm',
        'sale_crm',
        'base_location',
    ],
    'data': ['views/crm_lead.xml', ],
    'installable': True
}
