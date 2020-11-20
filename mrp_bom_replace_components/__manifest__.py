{
    'name': 'Manufacturing Bom Replace Components',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Replace in batch''',
    'depends': [
        'mrp',
    ],
    'data': [
        'views/bom_template.xml',
        'wizard/replace_bom_components.xml',
    ],
    'installable': True
}
