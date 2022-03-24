{
    'name': 'CRM Lead Number',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Automatically set a unique opportunity number",
    'depends': [
        'crm',
    ],
    'data': [
        'data/ir_sequence.xml',
        'data/ir_actions_server.xml',
        'views/crm_lead.xml',
    ],
    'installable': True
}
