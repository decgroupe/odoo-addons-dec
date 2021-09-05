{
    'name': 'Manufacturing Stock Operations',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Allow to open an advance view to edit moves like pickings",
    'depends': [
        'mrp',
        'sale_stock',
        'stock_assign',
    ],
    'data': ['views/mrp_production.xml', ],
    'installable': True
}
