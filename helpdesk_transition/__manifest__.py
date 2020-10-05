{
    'name': 'Help (transition)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Create helpdesk data from crm.helpdesk''',
    'depends': [
        'dec', # Added only to force create dummy smtp server
        'helpdesk_mgmt',
        'helpdesk_references',
    ],
    #'force_migration':'12.0.0.0.0',
    'data': [

    ],
    'installable': True
}
