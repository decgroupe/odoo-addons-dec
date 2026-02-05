{
    "name": "Project CRM Link",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "project",
        "project_identification",
        "project_typefast",
        "project_acl",
        "project_action_view",
        "crm",
        "crm_timesheet",  # OCA module
        "crm_lead_number",
        "web_m2x_options",
    ],
    "data": [
        "views/project_project.xml",
        "views/crm_lead.xml",
    ],
    "installable": True,
}
