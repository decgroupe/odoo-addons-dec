{
    'name': 'L10n FR Easy expense sheet (HE)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "French Localization for easy expense module",
    'depends': [
        'hr_expense_easy',
        'l10n_fr',
    ],
    'data': [],
    'force_post_init_hook': True,
    'post_init_hook': 'post_init_hook',
    'installable': True
}
