{
    'name': 'Project CRM Link',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Allow projects to be linked with an opportunity",
    'depends': [
        'project',
        'project_identification',
        'project_typefast',
        'project_acl',
        'crm',
        'crm_lead_number',
        'web_m2x_options',
    ],
    'data': [
        'views/project_project.xml',
        'views/crm_lead.xml',
    ],
    'installable': True
}
