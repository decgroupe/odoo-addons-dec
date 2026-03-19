# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import fields
from odoo.tests.common import TransactionCase


class TestProductPricelistHistory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Prepare shared records used to validate history tracing."""
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "History Product", "list_price": 100.0}
        )
        cls.category = cls.product.categ_id
        cls.other_category = cls.env["product.category"].create(
            {"name": "Other Category"}
        )
        cls.other_product = cls.env["product.product"].create(
            {"name": "Other Product", "list_price": 50.0}
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "History Pricelist"}
        )
        cls.rule = cls.env["product.pricelist.item"].create(
            {
                "name": "History Fixed Rule",
                "pricelist_id": cls.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "compute_price": "fixed",
                "fixed_price": 42.0,
            }
        )

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _compute_with_history(self, pricelist, product, qty):
        """Run price computation with history and return steps."""
        history = {"level": 0}
        uom = product.uom_id
        result = pricelist.with_context(history=history)._compute_price_rule(
            product,
            qty,
            uom=uom,
            date=fields.Datetime.now(),
        )
        price, rule_id = result[product.id]
        hkey = next(
            (k for k in history if isinstance(k, tuple) and k[0] == product),
            None,
        )
        steps = history[hkey]["steps"] if hkey else []
        return price, rule_id, steps

    # ------------------------------------------------------------------
    # graph building
    # ------------------------------------------------------------------

    def test_01_addto_history_builds_graph(self):
        """Ensure history steps and graph links are created."""
        history = {}
        key = "simple-key"
        pl = self.pricelist.with_context(history=history)
        s1 = pl._addto_history(key, "first step")
        s2 = pl._addto_history(
            key,
            "second step",
            last_state_id=s1,
        )
        pl._addto_history(key, indent=True)
        pl._addto_history(key, "third step")
        self.assertIn(key, history)
        self.assertEqual(
            history[key]["steps"][0],
            "first step",
        )
        self.assertEqual(
            history[key]["steps"][1],
            "second step",
        )
        self.assertEqual(
            history[key]["steps"][2],
            "  third step",
        )
        body = history[key]["graph"]["body"]
        self.assertTrue(any(f'{s1}["first step"]' in line for line in body))
        self.assertTrue(
            any(
                f'{s1}["first step"] -->' f' {s2}["second step"]' in line
                for line in body
            ),
        )

    # ------------------------------------------------------------------
    # fixed price rule (basic)
    # ------------------------------------------------------------------

    def test_02_compute_price_rule_populates_history(self):
        """Fixed price rule records history trace."""
        price, rule_id, steps = self._compute_with_history(
            self.pricelist,
            self.product,
            1.0,
        )
        self.assertEqual(price, 42.0)
        self.assertEqual(rule_id, self.rule.id)
        self.assertTrue(any("Using" in s for s in steps))
        self.assertTrue(any("Returns" in s for s in steps))

    # ------------------------------------------------------------------
    # min_quantity filtering
    # ------------------------------------------------------------------

    def test_03_min_quantity_excludes_rule(self):
        """Rule with min_quantity > ordered qty is skipped."""
        pl = self.env["product.pricelist"].create(
            {"name": "MinQty PL"},
        )
        self.env["product.pricelist.item"].create(
            {
                "name": "MinQty Rule",
                "pricelist_id": pl.id,
                "applied_on": "1_product",
                "product_tmpl_id": (self.product.product_tmpl_id.id),
                "compute_price": "fixed",
                "fixed_price": 10.0,
                "min_quantity": 100,
            },
        )
        _price, rule_id, steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        # rule not applicable so fallback price is used
        self.assertFalse(rule_id)
        self.assertTrue(any("ignored" in s for s in steps))

    def test_04_min_quantity_includes_rule(self):
        """Rule with min_quantity <= ordered qty is applied."""
        pl = self.env["product.pricelist"].create(
            {"name": "MinQty OK PL"},
        )
        rule = self.env["product.pricelist.item"].create(
            {
                "name": "MinQty OK Rule",
                "pricelist_id": pl.id,
                "applied_on": "1_product",
                "product_tmpl_id": (self.product.product_tmpl_id.id),
                "compute_price": "fixed",
                "fixed_price": 5.0,
                "min_quantity": 10,
            },
        )
        price, rule_id, _steps = self._compute_with_history(
            pl,
            self.product,
            10.0,
        )
        self.assertEqual(price, 5.0)
        self.assertEqual(rule_id, rule.id)

    # ------------------------------------------------------------------
    # applied_on = 2_product_category
    # ------------------------------------------------------------------

    def test_05_applied_on_category_match(self):
        """Category rule matches when product is in the category."""
        pl = self.env["product.pricelist"].create(
            {"name": "Categ PL"},
        )
        rule = self.env["product.pricelist.item"].create(
            {
                "name": "Categ Rule",
                "pricelist_id": pl.id,
                "applied_on": "2_product_category",
                "categ_id": self.category.id,
                "compute_price": "fixed",
                "fixed_price": 77.0,
            },
        )
        price, rule_id, _steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertEqual(price, 77.0)
        self.assertEqual(rule_id, rule.id)

    def test_06_applied_on_category_mismatch(self):
        """Category rule is skipped for a mismatched category."""
        pl = self.env["product.pricelist"].create(
            {"name": "Categ Miss PL"},
        )
        self.env["product.pricelist.item"].create(
            {
                "name": "Wrong Categ Rule",
                "pricelist_id": pl.id,
                "applied_on": "2_product_category",
                "categ_id": self.other_category.id,
                "compute_price": "fixed",
                "fixed_price": 99.0,
            },
        )
        _price, rule_id, steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertFalse(rule_id)
        self.assertTrue(any("No suitable rule found" in s for s in steps))

    # ------------------------------------------------------------------
    # applied_on = 0_product_variant
    # ------------------------------------------------------------------

    def test_07_applied_on_variant_match(self):
        """Variant-specific rule matches the correct variant."""
        pl = self.env["product.pricelist"].create(
            {"name": "Variant PL"},
        )
        rule = self.env["product.pricelist.item"].create(
            {
                "name": "Variant Rule",
                "pricelist_id": pl.id,
                "applied_on": "0_product_variant",
                "product_id": self.product.id,
                "compute_price": "fixed",
                "fixed_price": 33.0,
            },
        )
        price, rule_id, _steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertEqual(price, 33.0)
        self.assertEqual(rule_id, rule.id)

    def test_08_applied_on_variant_mismatch(self):
        """Variant-specific rule is skipped for wrong variant."""
        pl = self.env["product.pricelist"].create(
            {"name": "Variant Miss PL"},
        )
        self.env["product.pricelist.item"].create(
            {
                "name": "Other Variant Rule",
                "pricelist_id": pl.id,
                "applied_on": "0_product_variant",
                "product_id": self.other_product.id,
                "compute_price": "fixed",
                "fixed_price": 11.0,
            },
        )
        _price, rule_id, steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertFalse(rule_id)
        self.assertTrue(any("No suitable rule found" in s for s in steps))

    # ------------------------------------------------------------------
    # applied_on = 1_product  (template mismatch)
    # ------------------------------------------------------------------

    def test_09_applied_on_template_mismatch(self):
        """Template rule is skipped for a different product."""
        pl = self.env["product.pricelist"].create(
            {"name": "Tmpl Miss PL"},
        )
        self.env["product.pricelist.item"].create(
            {
                "name": "Other Tmpl Rule",
                "pricelist_id": pl.id,
                "applied_on": "1_product",
                "product_tmpl_id": (self.other_product.product_tmpl_id.id),
                "compute_price": "fixed",
                "fixed_price": 22.0,
            },
        )
        _price, rule_id, steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertFalse(rule_id)
        self.assertTrue(any("No suitable rule found" in s for s in steps))

    # ------------------------------------------------------------------
    # compute_price = percentage
    # ------------------------------------------------------------------

    def test_10_percentage_price(self):
        """Percentage discount rule traces correctly."""
        pl = self.env["product.pricelist"].create(
            {"name": "Pct PL"},
        )
        rule = self.env["product.pricelist.item"].create(
            {
                "name": "Pct Rule",
                "pricelist_id": pl.id,
                "applied_on": "1_product",
                "product_tmpl_id": (self.product.product_tmpl_id.id),
                "compute_price": "percentage",
                "percent_price": 20.0,
            },
        )
        # list_price=100, 20% off => 80
        price, rule_id, steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertAlmostEqual(price, 80.0)
        self.assertEqual(rule_id, rule.id)
        self.assertTrue(any("percentage" in s for s in steps))

    # ------------------------------------------------------------------
    # compute_price = formula  (discount + surcharge + rounding)
    # ------------------------------------------------------------------

    def test_11_formula_discount(self):
        """Formula rule with discount traces the discount step."""
        pl = self.env["product.pricelist"].create(
            {"name": "Formula PL"},
        )
        rule = self.env["product.pricelist.item"].create(
            {
                "name": "Formula Discount Rule",
                "pricelist_id": pl.id,
                "applied_on": "1_product",
                "product_tmpl_id": (self.product.product_tmpl_id.id),
                "compute_price": "formula",
                "base": "list_price",
                "price_discount": 10.0,
            },
        )
        # list_price=100, 10% discount => 90
        price, rule_id, steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertAlmostEqual(price, 90.0)
        self.assertEqual(rule_id, rule.id)
        self.assertTrue(any("discounted" in s for s in steps))

    def test_12_formula_surcharge(self):
        """Formula rule with surcharge traces surcharge step."""
        pl = self.env["product.pricelist"].create(
            {"name": "Surcharge PL"},
        )
        rule = self.env["product.pricelist.item"].create(
            {
                "name": "Surcharge Rule",
                "pricelist_id": pl.id,
                "applied_on": "1_product",
                "product_tmpl_id": (self.product.product_tmpl_id.id),
                "compute_price": "formula",
                "base": "list_price",
                "price_discount": 0,
                "price_surcharge": 5.0,
            },
        )
        # list_price=100, surcharge +5 => 105
        price, rule_id, steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertAlmostEqual(price, 105.0)
        self.assertEqual(rule_id, rule.id)
        self.assertTrue(any("surcharge" in s for s in steps))

    def test_13_formula_rounding(self):
        """Formula rule with rounding traces rounding step."""
        pl = self.env["product.pricelist"].create(
            {"name": "Round PL"},
        )
        rule = self.env["product.pricelist.item"].create(
            {
                "name": "Round Rule",
                "pricelist_id": pl.id,
                "applied_on": "1_product",
                "product_tmpl_id": (self.product.product_tmpl_id.id),
                "compute_price": "formula",
                "base": "list_price",
                "price_discount": 15.0,
                "price_round": 10.0,
            },
        )
        # list_price=100, 15% off=85, round to 10 => 90
        price, rule_id, steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertAlmostEqual(price, 90.0)
        self.assertEqual(rule_id, rule.id)
        self.assertTrue(any("rounded" in s for s in steps))

    def test_14_formula_min_margin(self):
        """Formula rule with min margin traces margin step."""
        pl = self.env["product.pricelist"].create(
            {"name": "MinMargin PL"},
        )
        rule = self.env["product.pricelist.item"].create(
            {
                "name": "MinMargin Rule",
                "pricelist_id": pl.id,
                "applied_on": "1_product",
                "product_tmpl_id": (self.product.product_tmpl_id.id),
                "compute_price": "formula",
                "base": "list_price",
                "price_discount": 50.0,
                "price_min_margin": 60.0,
                # to validate constraint price_min_margin <= price_max_margin
                "price_max_margin": 999.0,
            },
        )
        # list_price=100, 50% off=50, min margin=60 => 160
        price, rule_id, steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertAlmostEqual(price, 160.0)
        self.assertEqual(rule_id, rule.id)
        self.assertTrue(any("minimum margin" in s for s in steps))

    def test_15_formula_max_margin(self):
        """Formula rule with max margin traces margin step."""
        pl = self.env["product.pricelist"].create(
            {"name": "MaxMargin PL"},
        )
        rule = self.env["product.pricelist.item"].create(
            {
                "name": "MaxMargin Rule",
                "pricelist_id": pl.id,
                "applied_on": "1_product",
                "product_tmpl_id": (self.product.product_tmpl_id.id),
                "compute_price": "formula",
                "base": "list_price",
                "price_discount": 0,
                "price_surcharge": 10.0,
                "price_max_margin": 5.0,
                # to validate constraint price_min_margin <= price_max_margin
                "price_min_margin": 0.0,
            },
        )
        # list_price=100, no discount=100, surcharge=110, max margin=5 => 105
        price, rule_id, steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertAlmostEqual(price, 105.0)
        self.assertEqual(rule_id, rule.id)
        self.assertTrue(any("maximum margin" in s for s in steps))

    # ------------------------------------------------------------------
    # base price = another pricelist
    # ------------------------------------------------------------------

    def test_16_base_pricelist(self):
        """Formula based on another pricelist traces delegation."""
        base_pl = self.env["product.pricelist"].create(
            {"name": "Base PL"},
        )
        self.env["product.pricelist.item"].create(
            {
                "name": "Base Fixed",
                "pricelist_id": base_pl.id,
                "applied_on": "1_product",
                "product_tmpl_id": (self.product.product_tmpl_id.id),
                "compute_price": "fixed",
                "fixed_price": 200.0,
            },
        )
        pl = self.env["product.pricelist"].create(
            {"name": "Delegating PL"},
        )
        rule = self.env["product.pricelist.item"].create(
            {
                "name": "Delegate Rule",
                "pricelist_id": pl.id,
                "applied_on": "1_product",
                "product_tmpl_id": (self.product.product_tmpl_id.id),
                "compute_price": "formula",
                "base": "pricelist",
                "base_pricelist_id": base_pl.id,
                "price_discount": 0,
            },
        )
        price, rule_id, steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertAlmostEqual(price, 200.0)
        self.assertEqual(rule_id, rule.id)
        self.assertTrue(any("another pricelist" in s for s in steps))

    # ------------------------------------------------------------------
    # base price = standard_price (cost)
    # ------------------------------------------------------------------

    def test_17_base_standard_price(self):
        """Formula based on cost price traces the base."""
        self.product.standard_price = 30.0
        pl = self.env["product.pricelist"].create(
            {"name": "Cost PL"},
        )
        rule = self.env["product.pricelist.item"].create(
            {
                "name": "Cost Rule",
                "pricelist_id": pl.id,
                "applied_on": "1_product",
                "product_tmpl_id": (self.product.product_tmpl_id.id),
                "compute_price": "formula",
                "base": "standard_price",
                "price_markup": 10.0,
            },
        )
        # cost=30, markup 10% => price=30+3=33
        price, rule_id, steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertAlmostEqual(price, 33.0)
        self.assertEqual(rule_id, rule.id)
        self.assertTrue(any("standard_price" in s for s in steps))

    # ------------------------------------------------------------------
    # no suitable rule  (all-products rule for different product)
    # ------------------------------------------------------------------

    def test_18_no_suitable_rule(self):
        """When no rule matches, history records the fallback."""
        pl = self.env["product.pricelist"].create(
            {"name": "Empty PL"},
        )
        _price, rule_id, steps = self._compute_with_history(
            pl,
            self.product,
            1.0,
        )
        self.assertFalse(rule_id)
        self.assertTrue(any("No rules loaded" in s for s in steps))
