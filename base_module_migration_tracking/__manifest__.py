{
    'name': 'Module Migration Tracking',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Add fields to track individual migration status",
    'depends': [
        'base',
        'mail',
        'web_tree_dynamic_colored_field',
    ],
    'data': [
        'views/assets.xml',
        'views/ir_module.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True
}
