# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSalePrices(TransactionCase):
    """Tests for the sale_prices module.

    Verifies that sale order line purchase_price is computed from
    default_purchase_price (product_prices) instead of standard_price.
    """

    @classmethod
    def setUpClass(cls):
        """Set up shared fixtures: partner, products and a basic pricelist."""
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.supplier = cls.env["res.partner"].create({"name": "Test Supplier"})
        # product with a standard_price distinct from any seller price
        cls.product = cls.env["product.product"].create(
            {
                "name": "Sale Prices Test Product",
                "standard_price": 10.0,
                "list_price": 25.0,
                "type": "consu",
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_unit.id,
            }
        )

    def _create_so_line(self, product=None):
        """Create a sale order with one line for the given product."""
        product = product or self.product
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [Command.create({"product_id": product.id})],
            }
        )
        return so.order_line[0]

    def test_01_get_purchase_price_returns_default_purchase_price(self):
        """_get_purchase_price returns the product's default_purchase_price."""
        line = self._create_so_line()
        self.assertEqual(
            line._get_purchase_price(),
            line.product_id.default_purchase_price,
        )

    def test_02_purchase_price_uses_standard_price_when_no_seller(self):
        """Without a seller, purchase_price falls back to standard_price."""
        # ensure no seller is set on the product
        self.product.seller_ids = [Command.clear()]
        self.product.invalidate_recordset()
        line = self._create_so_line()
        # default_purchase_price falls back to standard_price when no seller
        self.assertAlmostEqual(line.purchase_price, self.product.standard_price)

    def test_03_purchase_price_uses_seller_price_instead_of_standard_price(self):
        """With a seller, purchase_price uses the seller's price, not standard_price."""
        seller_price = 30.0
        # create a supplierinfo so main_seller_id is set
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": seller_price,
                "product_uom": self.uom_unit.id,
            }
        )
        self.product.invalidate_recordset()
        tmpl = self.product.product_tmpl_id
        tmpl.invalidate_recordset()
        # verify main_seller_id is set and default_purchase_price differs from cost
        self.assertTrue(tmpl.main_seller_id)
        self.assertAlmostEqual(tmpl.default_purchase_price, seller_price)
        self.assertNotAlmostEqual(
            tmpl.default_purchase_price, self.product.standard_price
        )
        line = self._create_so_line()
        # purchase_price must match the seller price, not standard_price
        self.assertAlmostEqual(line.purchase_price, seller_price)
        self.assertNotAlmostEqual(line.purchase_price, self.product.standard_price)

    def test_04_purchase_price_zero_when_no_cost(self):
        """When default_purchase_price is 0, purchase_price on the line is 0."""
        product_zero = self.env["product.product"].create(
            {
                "name": "Zero Cost Product",
                "standard_price": 0.0,
                "list_price": 5.0,
                "type": "consu",
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
            }
        )
        # no seller → default_purchase_price falls back to standard_price = 0
        self.assertAlmostEqual(product_zero.default_purchase_price, 0.0)
        line = self._create_so_line(product=product_zero)
        self.assertAlmostEqual(line.purchase_price, 0.0)

    def test_05_no_product_clears_purchase_price(self):
        """When product_id is unset, purchase_price is forced to 0."""
        line = self._create_so_line()
        # unset product and force recompute
        line.product_id = False
        line._compute_purchase_price()
        self.assertAlmostEqual(line.purchase_price, 0.0)

    def test_06_uom_conversion_applies_to_purchase_price(self):
        """When line UoM differs from product UoM, cost is converted."""
        uom_dozen = self.env.ref("uom.product_uom_dozen")
        seller_price_per_unit = 6.0
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": seller_price_per_unit,
                "product_uom": self.uom_unit.id,
            }
        )
        self.product.invalidate_recordset()
        self.product.product_tmpl_id.invalidate_recordset()
        # create SO line with dozen as the order UoM
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom": uom_dozen.id,
                        }
                    )
                ],
            }
        )
        line = so.order_line[0]
        # cost per dozen should be 12× the per-unit price (unit→dozen conversion)
        expected = self.uom_unit._compute_price(
            self.product.product_tmpl_id.default_purchase_price,
            uom_dozen,
        )
        self.assertAlmostEqual(line.purchase_price, expected)
