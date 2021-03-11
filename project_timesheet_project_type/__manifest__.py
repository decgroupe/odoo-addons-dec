{
    'name': 'Project Type for Timesheet',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': "Add project type to filter view",
    'depends': [
        'hr_timesheet',
        'project_category',
    ],
    'data': ['views/hr_timesheet.xml', ],
    'installable': True
}
