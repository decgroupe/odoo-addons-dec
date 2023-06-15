{
    "name": "Manufacturing Bom Replace Components",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "mrp",
        "mrp_bom_supplier",
        "mrp_buy_consu",
        "queue_job",
        "web_base_view",
    ],
    "data": [
        "views/bom_template.xml",
        "wizard/replace_bom_components.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
