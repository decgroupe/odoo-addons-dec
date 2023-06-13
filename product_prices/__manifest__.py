{
    "name": "Product prices",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
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
        "views/assets.xml",
        "views/product_template.xml",
        "wizard/product_price_graph.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
