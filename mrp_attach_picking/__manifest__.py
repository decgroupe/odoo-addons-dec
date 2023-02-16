{
    'name': 'Manufacturing Attach Picking',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        'When a manufacturing order is created manually, it will be '
        'moved to stock location. But sometimes you need to assign it to an'
        'existing delivery picking',
    'depends': ['mrp', ],
    'data': [
        'wizard/mrp_attach_picking.xml',
        'views/mrp_production.xml',
    ],
    'installable': True
}
