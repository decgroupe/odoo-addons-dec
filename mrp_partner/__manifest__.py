{
    "name": "Production Partner",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "base_location",
        "mrp",
        "mrp_stage",  # To add partner data on kanban view
    ],
    "data": [
        "views/mrp_production.xml",
    ],
    "installable": True,
}
