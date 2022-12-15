{
    'name': 'Sale Timesheet Project',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Sales',
    'summary':
        "Auto create project on validate and add a button to create "
        "a timesheet before validating the sale order",
    'depends':
        [
            'project_identification',
            'sale_timesheet',
            'sale_delivery_date',
            'sale_action_view',
        ],
    'data':
        [
            'views/sale_order.xml',
            'views/project_project.xml',
            'views/project_task.xml',
        ],
    'installable': True
}
