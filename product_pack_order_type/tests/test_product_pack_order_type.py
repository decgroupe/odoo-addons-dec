# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

import logging

from odoo import Command
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestProductPackOrderType(TransactionCase):
    def _create_product(self, data):
        product = self.env["product.product"].create(data)
        # ensure clean context
        return self.env["product.product"].browse(product.id)

    def setUp(self):
        super().setUp()

        self.product_pack = self._create_product(
            {
                "name": "MyPack",
                "pack_ok": True,
                "pack_order_type": "all",
                "pack_type": "detailed",
                "pack_component_price": "ignored",
            }
        )
        self.item_a = self._create_product({"name": "ItemA"})
        self.item_b = self._create_product({"name": "ItemB"})
        self.item_c = self._create_product({"name": "ItemC"})
        _logger.info(
            "Pack Product Template ID: %s", self.product_pack.product_tmpl_id.id
        )
        _logger.info("Pack Product ID: %s", self.product_pack.id)
        self.product_pack.pack_line_ids = [
            Command.create({"product_id": self.item_a.id, "quantity": 2}),
            Command.create({"product_id": self.item_b.id, "quantity": 3}),
            Command.create({"product_id": self.item_c.id, "quantity": 4}),
        ]

    def test_01_copy_pack_with_components(self):
        self.assertEqual(len(self.product_pack.pack_line_ids), 3)
        # copying a variant is not supported, only copying the template is supported
        pack_tmpl_copy = self.product_pack.product_tmpl_id.copy()
        pack_copy = pack_tmpl_copy.product_variant_id
        self.assertEqual(len(pack_copy.pack_line_ids), 3)
        for line in pack_copy.pack_line_ids:
            self.assertEqual(line.parent_product_id, pack_copy)

    def _create_orders(self):
        customer = self.env["res.partner"].create({"name": "Customer"})
        vendor = self.env["res.partner"].create({"name": "Vendor"})
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": customer.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product_pack.id, "product_uom_qty": 1}
                    ),
                ],
            }
        )
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": vendor.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product_pack.id, "product_uom_qty": 1}
                    ),
                ],
            }
        )
        return sale_order, purchase_order

    def test_02_pack_order_type_all(self):
        sale_order, purchase_order = self._create_orders()
        self.assertEqual(len(sale_order.order_line), 4)
        self.assertEqual(len(purchase_order.order_line), 4)

    def test_03_pack_order_type_sale(self):
        self.product_pack.pack_order_type = "sale"
        sale_order, purchase_order = self._create_orders()
        self.assertEqual(len(sale_order.order_line), 4)
        self.assertEqual(len(purchase_order.order_line), 1)

    def test_04_pack_order_type_purchase(self):
        self.product_pack.pack_order_type = "purchase"
        sale_order, purchase_order = self._create_orders()
        self.assertEqual(len(sale_order.order_line), 1)
        self.assertEqual(len(purchase_order.order_line), 4)
