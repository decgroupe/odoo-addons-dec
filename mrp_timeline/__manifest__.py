{
    'name': 'Manufacturing timeline',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': "Timeline view for production",
    'depends': [
        'mrp',
        'mrp_workcenter',
        'web_timeline',
    ],
    "data": [
        "templates/assets.xml",
        "views/mrp_production.xml",
    ],
    'installable': True
}
