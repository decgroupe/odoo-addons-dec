{
    'name': 'Manufacturing Project Auto',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': 'Automatically create or link project',
    'depends': [
        'project_identification',
        'mrp_project',
        'mrp_sale',
    ],
    'data': ['views/mrp_production.xml', ],
    'installable': True
}
