{
    'name': 'Software account',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Manage software accounts (google, steam, etc.)''',
    'depends': [
        'base',
        'product',
        'mrp',
        'software',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'views/software_account.xml',
            'views/software_account_supplier.xml',
            'views/menu.xml',
            'report/software_account.xml',
        ],
    'installable': True
}
