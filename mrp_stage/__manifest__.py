{
    'name': 'Manufacturing Stages',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Computed stage based on existing state and other data",
    'depends': [
        'mrp',
        'mrp_picked_rate',
        'web_kanban_draggable',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'data/mail_activity_type.xml',
            'data/mrp_production_stage.xml',
            'views/assets.xml',
            'views/mrp_production.xml',
        ],
    'installable': True
}
