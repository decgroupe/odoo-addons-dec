{
    'name': 'Merge Accounts',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin ',
    'website': 'https://www.decgroupe.com',
    'depends': [
        'account',
        'deltatech_merge',
    ],
    'data': [
        'security/res_groups.xml',
        'wizard/merge_account_tax.xml',
        'wizard/merge_account_account_tag.xml',
    ],
    'installable': True
}
