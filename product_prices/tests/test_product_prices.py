# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestProductPrices(TransactionCase):
    """Test price tracking, computed fields, and pricelist bypass on products."""

    @classmethod
    def setUpClass(cls):
        """Create shared product and pricelist records."""
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.product_tmpl = cls.env["product.template"].create(
            {
                "name": "Price Test Product",
                "list_price": 100.0,
                "standard_price": 50.0,
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_unit.id,
            }
        )
        cls.product = cls.product_tmpl.product_variant_id

    # ------------------------------------------------------------------
    # write tracking – product.product
    # ------------------------------------------------------------------

    def test_01_product_write_list_price_tracking(self):
        """Writing list_price on product.product records audit fields."""
        before = fields.Datetime.now()
        self.product.write({"list_price": 200.0})
        self.assertTrue(
            self.product.price_write_date >= before,
        )
        self.assertEqual(
            self.product.price_write_uid.id,
            self.env.user.id,
        )

    def test_02_product_write_standard_price_tracking(self):
        """Writing standard_price on product.product records audit."""
        before = fields.Datetime.now()
        self.product.write({"standard_price": 60.0})
        self.assertTrue(
            self.product.standard_price_write_date >= before,
        )
        self.assertEqual(
            self.product.standard_price_write_uid.id,
            self.env.user.id,
        )

    # ------------------------------------------------------------------
    # write tracking – product.template
    # ------------------------------------------------------------------

    def test_03_template_write_list_price_tracking(self):
        """Writing list_price on product.template records audit."""
        before = fields.Datetime.now()
        self.product_tmpl.write({"list_price": 300.0})
        self.assertTrue(
            self.product_tmpl.price_write_date >= before,
        )
        self.assertEqual(
            self.product_tmpl.price_write_uid.id,
            self.env.user.id,
        )

    def test_04_template_write_standard_price_tracking(self):
        """Writing standard_price on template records audit."""
        before = fields.Datetime.now()
        self.product_tmpl.write({"standard_price": 70.0})
        self.assertTrue(
            self.product_tmpl.standard_price_write_date >= before,
        )
        self.assertEqual(
            self.product_tmpl.standard_price_write_uid.id,
            self.env.user.id,
        )

    # ------------------------------------------------------------------
    # same_uom computed field
    # ------------------------------------------------------------------

    def test_05_same_uom_true(self):
        """same_uom is True when uom_id == uom_po_id."""
        self.assertTrue(self.product_tmpl.same_uom)

    def test_06_same_uom_false(self):
        """same_uom is False when purchase UoM differs."""
        self.product_tmpl.uom_po_id = self.uom_dozen
        self.assertFalse(self.product_tmpl.same_uom)

    # ------------------------------------------------------------------
    # standard_price_po_uom compute / inverse
    # ------------------------------------------------------------------

    def test_07_standard_price_po_uom_same_uom(self):
        """When UoMs are the same, po_uom price equals cost."""
        self.assertAlmostEqual(
            self.product_tmpl.standard_price_po_uom,
            self.product_tmpl.standard_price,
        )

    def test_08_standard_price_po_uom_different_uom(self):
        """Cost is converted when purchase UoM differs."""
        self.product_tmpl.uom_po_id = self.uom_dozen
        # 1 dozen = 12 units → cost per dozen = 50 * 12 = 600
        self.assertAlmostEqual(
            self.product_tmpl.standard_price_po_uom,
            600.0,
        )

    def test_09_set_standard_price_po_uom(self):
        """Inverse converts po_uom price back to unit cost."""
        self.product_tmpl.uom_po_id = self.uom_dozen
        # set po_uom price to 120 → unit cost = 120 / 12 = 10
        self.product_tmpl.standard_price_po_uom = 120.0
        self.product_tmpl._set_standard_price_po_uom()
        self.assertAlmostEqual(
            self.product_tmpl.standard_price,
            10.0,
        )

    # ------------------------------------------------------------------
    # default purchase price (no seller)
    # ------------------------------------------------------------------

    def test_10_default_purchase_price_no_seller(self):
        """Without main_seller_id, purchase price falls back to cost."""
        self.product_tmpl._compute_default_purchase_price()
        self.assertAlmostEqual(
            self.product_tmpl.default_purchase_price,
            self.product_tmpl.standard_price,
        )
        self.assertTrue(
            self.product_tmpl.default_purchase_price_graph,
        )

    # ------------------------------------------------------------------
    # default sell price
    # ------------------------------------------------------------------

    def test_11_default_sell_price_fallback(self):
        """Without a partner pricelist, sell price falls back to list."""
        self.product_tmpl._compute_default_sell_price()
        self.assertTrue(
            self.product_tmpl.default_sell_price_graph,
        )

    # ------------------------------------------------------------------
    # pricelist bypass
    # ------------------------------------------------------------------

    def test_12_bypass_creates_pricelist_item(self):
        """Enabling bypass creates a pricelist item."""
        self.env["product.pricelist"].create(
            {"name": "Sale PL", "type": "sale"},
        )
        self.product_tmpl.write({"pricelist_bypass": True})
        self.assertTrue(
            self.product_tmpl.pricelist_bypass_item,
        )

    def test_13_bypass_removes_pricelist_item(self):
        """Disabling bypass removes the pricelist item."""
        self.env["product.pricelist"].create(
            {"name": "Sale PL2", "type": "sale"},
        )
        self.product_tmpl.write({"pricelist_bypass": True})
        self.assertTrue(
            self.product_tmpl.pricelist_bypass_item,
        )
        self.product_tmpl.write({"pricelist_bypass": False})

    def test_14_bypass_no_sale_pricelist_raises(self):
        """Bypass raises UserError when no sale pricelist exists."""
        # make sure no sale pricelist is available
        self.env["product.pricelist"].search([("type", "=", "sale")]).unlink()
        with self.assertRaises(UserError):
            self.product_tmpl.update_bypass(state=True)

    # ------------------------------------------------------------------
    # open_price_graph actions
    # ------------------------------------------------------------------

    def test_15_product_open_price_graph(self):
        """open_price_graph on product returns an action dict."""
        action = self.product.open_price_graph()
        self.assertIn("context", action)

    def test_16_template_open_price_graph(self):
        """open_price_graph on template delegates to variant."""
        action = self.product_tmpl.open_price_graph()
        self.assertIn("context", action)

    # ------------------------------------------------------------------
    # wizard default_get
    # ------------------------------------------------------------------

    def test_17_wizard_default_get(self):
        """Wizard populates product_id from context."""
        Wizard = self.env["product.price.graph"].with_context(
            active_model="product.product",
            active_ids=[self.product.id],
        )
        defaults = Wizard.default_get(["product_id"])
        self.assertEqual(
            defaults.get("product_id"),
            self.product.id,
        )

    def test_18_wizard_default_get_no_product(self):
        """Wizard without matching context returns no product."""
        Wizard = self.env["product.price.graph"].with_context(
            active_model="res.partner",
            active_ids=[1],
        )
        defaults = Wizard.default_get(["product_id"])
        self.assertFalse(defaults.get("product_id"))

    # ------------------------------------------------------------------
    # default purchase price with seller
    # ------------------------------------------------------------------

    def test_19_default_purchase_price_with_seller(self):
        """With main_seller_id, purchase price comes from seller."""
        partner = self.env["res.partner"].create({"name": "Supplier"})
        self.env["product.supplierinfo"].create(
            {
                "partner_id": partner.id,
                "product_tmpl_id": self.product_tmpl.id,
                "price": 42.0,
            }
        )
        self.product_tmpl.invalidate_recordset()
        self.assertTrue(self.product_tmpl.main_seller_id)
        self.product_tmpl._compute_default_purchase_price()
        self.assertAlmostEqual(
            self.product_tmpl.default_purchase_price,
            self.product_tmpl.main_seller_id.list_price_unit,
        )

    # ------------------------------------------------------------------
    # default sell price – no pricelist
    # ------------------------------------------------------------------

    def test_20_default_sell_price_no_pricelist(self):
        """Without property_product_pricelist, sell price falls back to list."""
        company = self.env.company
        company.partner_id.property_product_pricelist = False
        self.product_tmpl._compute_default_sell_price()
        self.assertAlmostEqual(
            self.product_tmpl.default_sell_price,
            self.product_tmpl.list_price,
        )
        self.assertTrue(self.product_tmpl.default_sell_price_graph)
