{
    'name': 'Help (transition)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Create helpdesk data from crm.helpdesk''',
    'depends': [
        'dec', # Added only to force create dummy
        'helpdesk_mgmt',
    ],
    'force_migration':'12.0.0.0.0',
    'data': [

    ],
    'installable': True
}
