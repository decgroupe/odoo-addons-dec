{
    "name": "Product Pricelist Sequence",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "product",
    ],
    "data": [
        "views/product_pricelist.xml",
        "views/product_pricelist_item.xml",
    ],
    "installable": True,
    "pre_init_hook": "rename_module",

}
