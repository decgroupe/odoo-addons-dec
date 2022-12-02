{
    'name': 'Partner Training',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Create and manage multiple educational training specialties",
    'depends': [
        'base',
        'contacts',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'views/res_partner_training.xml',
            'views/res_partner_training_specialty.xml',
            'views/res_partner.xml',
            'views/menu.xml',
        ],
    'installable': True
}
