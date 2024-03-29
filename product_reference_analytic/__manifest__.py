{
    'name': 'Product Reference Analytic',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Product reference analytic linking''',
    'depends':
        [
            'product_reference',
            'product_analytic',
            'account_analytic_parent',
        ],
    'data': [
        'data/account_analytic_account.xml',
        'views/ref_category.xml',
        'views/res_config_settings.xml',
    ],
    # 'force_post_init_hook': True,
    'post_init_hook': 'post_init',
    'installable': True
}
