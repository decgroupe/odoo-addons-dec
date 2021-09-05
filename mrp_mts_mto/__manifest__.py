{
    'name': 'Manufacturing MTS+MTO Rule Support',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "The procure method of generated raw moves will be adjusted "
        "to match the an existing MTS+MTO stock rule",
    'depends': [
        'mrp',
        'stock_mts_mto_rule',
    ],
    'data': [],
    'installable': True
}
