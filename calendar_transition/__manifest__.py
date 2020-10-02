{
    'name': 'Calendar (transition)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Transition only (OpenERP to Odoo)''',
    'depends': [
        'base',
        'calendar',
    ],
    'data': [],
    #'force_post_init_hook': True,
    'post_init_hook': 'post_init',
    'installable': True
}
