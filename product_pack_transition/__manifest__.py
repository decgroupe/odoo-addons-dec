{
    'name': 'Product Pack (transition)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Product pack backported model for transition:
- Rename product.pack.saleline to product.pack.line
- Service tracking forced to NO to avoid task creation 
''',
    'depends': [
        'product_pack',
        'sale_timesheet',
    ],
    # 'force_migration':'12.0.0.0.0',
    'data': [

    ],
    'installable': True
}
