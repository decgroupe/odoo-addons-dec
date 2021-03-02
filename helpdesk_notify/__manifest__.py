{
    'name': 'Helpdesk Notify',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        "Send internal e-mail when a new ticket is "
        "automatically created",
    'depends': ['helpdesk_mgmt', ],
    'data': ["data/mail_template.xml", ],
    'installable': True
}
