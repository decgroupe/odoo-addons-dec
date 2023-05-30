{
    'name': 'Manufacturing Project Task',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Service production tracking",
    'depends':
        [
            'mrp_project',
            'mrp_purchase',
            'mrp_stage',
            'sale_timesheet',
            'sale_timesheet_line_exclude',
            # 'sale_timesheet_task_exclude', [MIG] 14.0: Not needed anymore acoording to https://github.com/OCA/timesheet/pull/440#issuecomment-1235611830
            'project_action_view',
            'project_identification',
        ],
    'data': [
        'views/mrp_production.xml',
        'views/project_task.xml',
    ],
    'installable': True
}