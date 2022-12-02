{
    'name': 'Product Reference Price History',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Price history and reporting''',
    'depends': [
        'base',
        'mail',
        'product_reference',
        'purchase',
        'product_state_review',
        'product_prices',
        'mrp_bom_prices',
        'wizard_run',
    ],
    # 'force_migration':'12.0.0.0.0',
    'data':
        [
            'security/ir.model.access.csv',
            'views/ref_reference.xml',
            'views/ref_price.xml',
            'data/ref_reference_data.xml',
            'data/ref_reference_cron.xml',
            'wizard/reference_compute_material_cost.xml',
            'wizard/reference_generate_material_cost_report.xml',
            'wizard/menu.xml',
        ],
    'installable': True
}
