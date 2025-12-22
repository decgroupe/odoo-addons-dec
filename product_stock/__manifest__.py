{
    "name": "Product Stock",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "product",
        "stock",
    ],
    "data": [
        "views/product_product.xml",
    ],
    "installable": False,  # Stock inventory is now manage by stock.quant/stock.move (is_inventory) => Major refactoring
}
