{
    'name': 'Sale Timesheet Project',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'category': 'Sales',
    'summary':
        "Auto create project on validate and add a button to create "
        "a timesheet before validating the sale order",
    'depends': [
        'project_identification',
        'sale_timesheet_existing_project',
    ],
    'data': ['views/sale_order.xml', ],
    'installable': True
}
