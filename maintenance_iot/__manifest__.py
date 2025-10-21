{
    "name": "Maintenance IoT",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "base_maintenance",
        "base_maintenance_group",
        "auth_api_key",
        "maintenance_archive",
    ],
    "data": [
        "views/maintenance_request.xml",
        "data/template.xml",
    ],
    "installable": True,
}
