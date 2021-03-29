{
    'name': 'Users signature',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'category': 'Base',
    'summary': '''Text signature for reports''',
    'depends': [
        'base',
        'hr',
    ],
    'data':
        [
            'views/res_users.xml',
            'views/hr_employee.xml',
            'data/signature_template.xml',
            'security/ir.model.access.csv',
        ],
    'installable': True
}
