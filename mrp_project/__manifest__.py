{
    'name': 'Manufacturing Project',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': 'Add project linking support to production',
    'depends': [
        'mrp',
        'project',
    ],
    'data':
        [
            'data/analytic_account.xml',
            'views/mrp_production.xml',
            'views/project.xml',
        ],
    'installable': True
}
