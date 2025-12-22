{
    "name": "HR Timesheet Auto-fill",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "hr_timesheet",
        "project_timesheet_time_control",
    ],
    "data": [
        "views/account_analytic_line.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "hr_timesheet_autofill/static/src/scss/style.scss",
        ],
    },
    "installable": True,
}
