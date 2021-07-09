{
    'name': 'CRM Timesheet Project Context',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        "Disable Super-Manager needed to create a project",
    'depends': [
        'crm_timesheet',
        'project_acl',
    ],
    'data': [
        'views/crm_lead.xml',

    ],
    'installable': True
}
