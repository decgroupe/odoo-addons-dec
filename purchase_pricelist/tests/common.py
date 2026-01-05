# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo import Command
from odoo.tests.common import TransactionCase


class TestPurchasePricelistCommon(TransactionCase):
    def _create_supplier(self, name, pricelist_id, vals=None):
        if vals is None:
            vals = {}
        Partner = self.env["res.partner"]
        vals["supplier_rank"] = 10
        vals["specific_property_product_pricelist_purchase"] = pricelist_id.id
        if "name" not in vals:
            vals["name"] = name
        supplier = Partner.create(vals)
        return supplier

    def _create_pricelist_with_default_item(self, name, base, vals=None):
        if vals is None:
            vals = {}
        if "name" not in vals:
            vals["name"] = name
        if "type" not in vals:
            vals["type"] = "purchase"
        pricelist_id = self.pricelist_model.create(vals)
        self.pricelist_item_model.create(
            {
                "pricelist_id": pricelist_id.id,
                # "sequence": 5,
                "applied_on": "3_global",
                "compute_price": "formula",
                "base": base,
            }
        )
        return pricelist_id

    def _get_default_product_values(
        self, supplier_id, lst_price=1000, standard_price=800, seller_price=0
    ):
        return {
            "uom_id": self.env.ref("uom.product_uom_unit").id,
            "lst_price": lst_price,
            "standard_price": standard_price,
            "seller_ids": [
                Command.create(
                    {
                        "sequence": 1,
                        "partner_id": supplier_id.id,
                        "min_qty": 1.0,
                        "price": seller_price,
                    }
                )
            ],
        }

    def _create_product(self, name, vals=None):
        if vals is None:
            vals = {}
        if "name" not in vals:
            vals["name"] = name
        product_id = self.env["product.product"].create(vals)
        return product_id

    def _create_purchase_order(self, supplier_id, product_id):
        purchase_order_id = self.purchase_model.create(
            {
                "partner_id": supplier_id.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product_id.id,
                            "name": product_id.name,
                            "product_qty": 1.0,
                        }
                    )
                ],
            }
        )
        return purchase_order_id

    def setUp(self):
        super().setUp()
        self.purchase_model = self.env["purchase.order"]
        self.purchase_line_model = self.env["purchase.order.line"]
        self.pricelist_model = self.env["product.pricelist"]
        self.pricelist_item_model = self.env["product.pricelist.item"]
