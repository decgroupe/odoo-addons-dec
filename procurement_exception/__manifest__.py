{
    "name": "Procurement exception manager",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "stock",
        "procurement_log",
        "procurement_run_mto",  # to intercept `_action_confirm_one_move`
        "procurement_run_mts",  # to intercept `_action_cannot_reorder_product`
        "procurement_run_manufacture_warnings",  # to restore old warnings about no/empty BOM  # noqa: E501
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/procurement_exception.xml",
        "views/procurement_exception.xml",
        "views/res_config_settings.xml",
    ],
    "demo": [
        "demo/product_demo.xml",
    ],
    "installable": True,
}
