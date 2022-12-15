{
    'name': 'CRM Timesheet Identification',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Add extra data to identify opportunity entry",
    'depends': [
        'crm_timesheet',
        'crm_lead_identification',
    ],
    'data': ['views/account_analytic_line.xml', ],
    'installable': True
}
