{
    'name': 'Partner Commercial Fencing',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Add an option to hide business documents in portal "
        "to specific contacts",
    'depends': ['base', ],
    'data': [
        'views/partner.xml',
        'data/ir_rule.xml',
    ],
    'installable': True
}
