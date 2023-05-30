{
    "name": "HR Timesheet Exclude",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "hr_timesheet_autofill",
        "sale_timesheet_line_exclude",
        # 'sale_timesheet_task_exclude', [MIG] 14.0: Not needed anymore acoording to https://github.com/OCA/timesheet/pull/440#issuecomment-1235611830
    ],
    "data": [
        "views/project_task.xml",
        "views/project_project.xml",
        "views/account_analytic_line.xml",
    ],
    "installable": True,
}
