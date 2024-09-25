{
    "name": "MRP Portal",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "mrp",
        "auth_api_key",
        "base_sequence_first_number",
    ],
    "data": [
        "data/mail_data.xml",
        "data/template.xml",
        "views/mrp_production.xml",
        "report/mrp_report.xml",
    ],
    "installable": True,
}
