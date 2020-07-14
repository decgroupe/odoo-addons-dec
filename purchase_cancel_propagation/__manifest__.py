{
    'name': 'Purchase cancel propagation',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Choose between simple delete or delete and propagate to cancel procurement''',
    'depends': [
        'purchase_stock',
        'web_ir_actions_act_view_reload',
    ],
    'data': [
        'views/purchase_order.xml',
    ],
    'installable': True
}
