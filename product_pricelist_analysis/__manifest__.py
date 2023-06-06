{
    "name": "Product Pricelist Analysis",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "product",
        "product_pricelist_sequence",
        "purchase_pricelist",  # Needed for type sale/purchase
    ],
    "data": [
        "views/product_pricelist_item.xml",
        "views/product_pricelist.xml",
        "views/product_template.xml",
    ],
    "installable": True,
}
