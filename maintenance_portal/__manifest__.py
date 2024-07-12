{
    "name": "Maintenance Portal",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
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
