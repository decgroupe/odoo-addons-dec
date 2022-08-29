{
    'name': 'Sale Timesheet Project',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Sales',
    'summary':
        "Auto create project on validate and add a button to create "
        "a timesheet before validating the sale order",
    'depends': [
        'project_identification',
        'sale_timesheet_existing_project',
        'sale_delivery_date',
    ],
    'data': [
        'views/sale_order.xml',
        'views/project_project.xml',
        'views/project_task.xml',
    ],
    'installable': True
}
