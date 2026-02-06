{
    "name": "Product Public Code",
    "version": "18.0.1.0.1",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "product",
        # "product_state",  # for 'obsolete' state, soft-dependency
        "sale",
        "base_view_inheritance_extension",
    ],
    "data": [
        "views/product_template.xml",
        "views/product_product.xml",
        "views/sale_order.xml",
    ],
    "installable": True,
}
