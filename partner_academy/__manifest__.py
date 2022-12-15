{
    'name': 'Partner Academy',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Add an academy field to partner used to group educational "
        "partners",
    'depends': [
        'base',
        'contacts',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'views/res_partner.xml',
            'views/res_partner_academy.xml',
        ],
    'installable': True
}
