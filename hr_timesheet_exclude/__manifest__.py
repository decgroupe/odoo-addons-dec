{
    'name': 'HR Timesheet Exclude',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Select task/projects that should be excluded from analysis",
    'depends':
        [
            'hr_timesheet',
            'sale_timesheet_line_exclude',
            'sale_timesheet_task_exclude',
        ],
    'data':
        [
            'views/project_task.xml',
            'views/project_project.xml',
            'views/account_analytic_line.xml',
        ],
    'installable': True
}
