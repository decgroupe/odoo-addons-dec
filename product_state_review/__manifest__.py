{
    "name": "Product State (Quotation/Review)",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "product_state",
        "product_state_active",
    ],
    "data": [
        "data/product_state.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
