{
    "name": "Web Report Workflow",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "summary": "Report template improvements",
    "depends": [
        "web",
        "company_report",
        "l10n_fr",  # siret
    ],
    "assets": {
        "web.report_assets_common": [
            "web_report_workflow/static/src/scss/style.scss",
        ],
    },
    "data": [
        "views/report_templates.xml",
    ],
    "installable": True,
}
