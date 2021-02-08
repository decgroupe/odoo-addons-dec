{
    'name': 'Manufacturing Project',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
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
            'views/project_task.xml',
        ],
    'installable': True
}
