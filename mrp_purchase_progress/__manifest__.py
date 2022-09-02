{
    'name': 'Manufacturing Purchase Progress',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Analyse stock moves to find out if they are waiting for "
        "another move (meaning a purchase one in most cases)",
    'depends': [
        'mrp',
        'mrp_stage',
        'mrp_picked_rate',
        'purchase_stock',
    ],
    'data': [
        'data/mrp_production_cron.xml',
        'views/mrp_production.xml',
    ],
    'installable': True
}
