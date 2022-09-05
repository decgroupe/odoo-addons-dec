{
    'name': 'Manufacturing Picked Rate',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Reimplementation of picked_rate",
    'depends': [
        'mrp',
        'mrp_partner',
        'mrp_stage',
    ],
    'data': [
        'data/mrp_production_cron.xml',
        'data/mrp_production_stage.xml',
        'views/mrp_production.xml',
    ],
    "pre_init_hook": "rename_module",
    'installable': True
}
