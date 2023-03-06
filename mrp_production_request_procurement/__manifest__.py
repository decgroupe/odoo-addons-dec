{
    'name': 'MRP Production Request Procurement',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Allow customization of the procurement group assigned to MO",
    'depends': [
        'mrp',
        'mrp_production_request',
    ],
    'data':
        [
            'views/mrp_production.xml',
            'views/mrp_production_request.xml',
            'security/ir.model.access.csv',
        ],
    'installable': True
}
