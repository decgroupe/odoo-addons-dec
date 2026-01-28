{
    "name": "Product prices",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "web_widget_mermaid",
        "product",
        "product_seller",
        "product_pricelist_sequence",
        "product_pricelist_history",
        "product_pricelist_analysis",
        "purchase_pricelist",
        "purchase_pricelist_analysis",
    ],
    "data": [
        "views/product_template.xml",
        "wizard/product_price_graph.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_backend": [
            "product_prices/static/src/scss/style.scss",
        ],
    },
    "installable": True,
}
