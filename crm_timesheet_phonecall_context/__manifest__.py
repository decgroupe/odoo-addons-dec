{
    'name': 'CRM Timesheet Phonecall Context',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        "Fix missing default project when creating a phonecall",
    'depends': [
        'crm_timesheet',
        'crm_phonecall_timesheet',
    ],
    'data': [
        'views/account_analytic_line.xml',

    ],
    'installable': True
}
