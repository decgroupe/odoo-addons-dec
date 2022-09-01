{
    'name': 'Manufacturing Stages',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Computed stage based on existing state and other data",
    'depends': [
        'mrp',
        'web_kanban_draggable',
        'web_ir_actions_act_multi',
        'web_ir_actions_act_view_reload',
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
