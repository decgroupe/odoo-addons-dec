{
    "name": "CRM Timesheet Calendar Lead Context",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "crm_timesheet",
        "hr_timesheet_calendar_dec",  # includes hr_timesheet_autofill
        "project_crm_link",
    ],
    "data": [
        "views/account_analytic_line.xml",
    ],
    "installable": True,
}
