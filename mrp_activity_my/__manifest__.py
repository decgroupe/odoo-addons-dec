{
    'name': 'MRP My Activities',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Backport next activity workflow from Odoo 14.0 but use current"
        "user",
    'depends':
        [
            'mrp',
            'mrp_stage',
            'web_widget_mail_list_activity',
            'web',
            'mail_activity_my',
        ],
    'data': ['views/mrp_production.xml', ],
    'installable': True
}
