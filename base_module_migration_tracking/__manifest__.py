{
    "name": "Module Migration Tracking",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "base",
        "mail",
        "web_tree_dynamic_colored_field", # OCA: web
    ],
    "data": [
        "views/assets.xml",
        "views/ir_module.xml",
        "security/ir.model.access.csv",
    ],
    "installable": False,
}
