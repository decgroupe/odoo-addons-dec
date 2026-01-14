{
    "name": "Module Migration Tracking",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "base",
        "mail",
        "web_tree_dynamic_colored_field",  # OCA: web
    ],
    "data": [
        "views/ir_module.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_backend": [
            "base_module_migration_tracking/static/src/css/style.scss"
        ],
    },
    "installable": True,
}
