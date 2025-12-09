{
    "name": "MRP IoT",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
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
