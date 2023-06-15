{
    "name": "Production Partner",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "base_location",
        "mrp",
        "mrp_stage", # To add partner data on kanban view
    ],
    "data": [
        "views/mrp_production.xml",
    ],
    "installable": True,
}
