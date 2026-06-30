# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2026

import datetime

from odoo.tests.common import TransactionCase


class TestProductStockCommon(TransactionCase):
    """Shared fixtures and helpers for the product stock tests."""

    def setUp(self):
        """Prepare shared stock and product fixtures."""
        super().setUp()
        self.Product = self.env["product.product"]  # type: ignore[index]
        self.StockMove = self.env["stock.move"]  # type: ignore[index]
        self.StockQuant = self.env["stock.quant"]  # type: ignore[index]
        self.location_stock = self.env.ref("stock.stock_location_stock")
        self.location_customers = self.env.ref("stock.stock_location_customers")
        product_category = self.env.ref("product.product_category_all")
        self.product_storagebox = self.Product.create(
            {
                "name": "Storage Box",
                "is_storable": True,
                "categ_id": product_category.id,
            }
        )
        self.product_drawer = self.Product.create(
            {
                "name": "Drawer",
                "is_storable": True,
                "categ_id": product_category.id,
            }
        )
        self.product_flipover = self.Product.create(
            {
                "name": "Flipover",
                "is_storable": True,
                "categ_id": product_category.id,
            }
        )

    def _now(self):
        """Return the current timestamp without microseconds."""
        return datetime.datetime.now().replace(microsecond=0)

    def _create_stock_move(
        self, product, qty=10, location_id=None, location_dest_id=None
    ):
        """Create a stock move for the given product and locations."""
        location_id = location_id or self.location_stock
        location_dest_id = location_dest_id or self.location_customers
        return self.StockMove.create(
            {
                "name": "Test Move",
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": qty,
                "location_id": location_id.id,
                "location_dest_id": location_dest_id.id,
            }
        )

    def _adjust_inventory(self, location, products, quantities):
        """Apply inventory adjustments for the given products."""
        quant_model = self.StockQuant.with_context(inventory_mode=True)
        for product, qty in zip(products, quantities, strict=True):
            quant = quant_model.create(
                {
                    "product_id": product.id,
                    "location_id": location.id,
                    "inventory_quantity": qty,
                }
            )
            quant.action_apply_inventory()
