{
    'name': 'HR Leaves Requestable',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Request holidays before their are considered as valid",
    'depends': ['hr_holidays', ],
    'data': [
        'views/hr_leave_type.xml',
        'views/hr_leave_allocation.xml',
    ],
    'installable': True
}
