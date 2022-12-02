{
    'name': 'Users signature',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Base',
    'summary': '''Text signature for reports''',
    'depends': [
        'base',
        'hr',
    ],
    'data':
        [
            'views/res_users_signature_template.xml',
            'views/res_users.xml',
            'views/hr_employee.xml',
            'views/hr_department.xml',
            'data/signature_template.xml',
            'security/ir.model.access.csv',
        ],
    'installable': True
}
