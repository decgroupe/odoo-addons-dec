{
    'name': 'Website Contact',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Allow helpdesk data manipulation without user account",
    'depends': [
        'helpdesk_notify',
    ],
    'data':
        [
            'views/assets.xml',
            'views/helpdesk_ticket_category.xml',
            'templates/website_contact.xml',
        ],
    'installable': True
}
