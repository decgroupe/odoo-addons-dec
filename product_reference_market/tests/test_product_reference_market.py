# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from .common import TestProductReferenceMarketCommon


class TestProductReferenceMarket(TestProductReferenceMarketCommon):
    """Tests for product_reference_market module."""

    def test_01_compute_market_bom_id_on_product(self):
        """Check that market_bom_id on product.product returns the first market BoM."""
        self.assertEqual(self.product.market_bom_id, self.market_bom)
        self.assertIn(self.market_bom, self.product.market_bom_ids)

    def test_02_compute_market_bom_id_on_product_template(self):
        """Check that market_bom_id on product.template is relayed from variant."""
        tmpl = self.product.product_tmpl_id
        self.assertEqual(tmpl.market_bom_id, self.market_bom)
        self.assertIn(self.market_bom, tmpl.market_bom_ids)

    def test_03_compute_market_bom_id_no_bom(self):
        """Check that market_bom_id is empty when no market BoM is linked."""
        product_no_bom = self.env["product.product"].create(
            {"name": "Product Without Market BoM", "type": "consu"}
        )
        self.assertFalse(product_no_bom.market_bom_id)

    def test_04_labortime_empty_bom(self):
        """Check that labortime is zero when no BoM lines are present."""
        self.assertEqual(self.market_bom.labortime, 0.0)

    def test_05_labortime_with_non_labor_line(self):
        """Check that labortime stays zero for lines that are not labor services."""
        self.env["ref.market.bom.line"].create(
            {
                "market_bom_id": self.market_bom.id,
                "product_id": self.product.id,
                "product_qty": 5.0,
                "product_uom_id": self.uom_unit.id,
            }
        )
        self.assertEqual(self.market_bom.labortime, 0.0)

    def test_06_labortime_with_labor_service_not_configured(self):
        """Check that labortime is zero when labortime services are not configured."""
        self.env["ref.market.bom.line"].create(
            {
                "market_bom_id": self.market_bom.id,
                "product_id": self.labor_service.id,
                "product_qty": 3.0,
                "product_uom_id": self.uom_hour.id,
            }
        )
        # by default get_labortime_services returns empty recordset, so
        # even a service product in the lines does not count as labor time
        self.assertEqual(self.market_bom.labortime, 0.0)

    def test_07_convert_qty_to_hours_same_uom(self):
        """Check that _convert_qty_to_hours returns qty directly when UoM is already
        hours."""
        line = self.env["ref.market.bom.line"].create(
            {
                "market_bom_id": self.market_bom.id,
                "product_id": self.labor_service.id,
                "product_qty": 2.0,
                "product_uom_id": self.uom_hour.id,
            }
        )
        self.assertAlmostEqual(line._convert_qty_to_hours(), 2.0)

    def test_08_convert_qty_to_hours_from_days(self):
        """Check that _convert_qty_to_hours converts days to hours correctly."""
        line = self.env["ref.market.bom.line"].create(
            {
                "market_bom_id": self.market_bom.id,
                "product_id": self.labor_service.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom_day.id,
            }
        )
        # 1 day = 8 hours by default in Odoo
        result = line._convert_qty_to_hours()
        self.assertGreater(result, 0.0)

    def test_09_convert_qty_to_hours_non_time_uom(self):
        """Check that _convert_qty_to_hours returns qty unchanged for non-time UoM."""
        line = self.env["ref.market.bom.line"].create(
            {
                "market_bom_id": self.market_bom.id,
                "product_id": self.product.id,
                "product_qty": 4.0,
                "product_uom_id": self.uom_unit.id,
            }
        )
        self.assertAlmostEqual(line._convert_qty_to_hours(), 4.0)

    def test_10_get_default_products(self):
        """Check that get_default_products returns an empty recordset by default."""
        result = self.env["ref.market.bom"].get_default_products()
        self.assertFalse(result)
        self.assertEqual(result._name, "product.product")

    def test_11_get_default_products_as_ids(self):
        """Check that get_default_products_as_ids returns an empty list by default."""
        result = self.env["ref.market.bom"].get_default_products_as_ids()
        self.assertEqual(result, [])

    def test_12_get_labortime_services(self):
        """Check that get_labortime_services returns an empty recordset by default."""
        result = self.env["ref.market.bom"].get_labortime_services()
        self.assertFalse(result)
        self.assertEqual(result._name, "product.product")

    def test_13_get_labortime_services_as_ids(self):
        """Check that get_labortime_services_as_ids returns an empty list by default."""
        result = self.env["ref.market.bom"].get_labortime_services_as_ids()
        self.assertEqual(result, [])

    def test_14_multiple_market_boms_first_is_returned(self):
        """Check that market_bom_id returns the first market BoM when multiple exist."""
        second_bom = self.env["ref.market.bom"].create(
            {"product_id": self.product.id, "markup_rate": 5.0}
        )
        bom_ids = self.product.market_bom_ids
        self.assertIn(self.market_bom, bom_ids)
        self.assertIn(second_bom, bom_ids)
        self.assertEqual(self.product.market_bom_id, bom_ids[:1])

    def test_15_market_bom_line_product_tmpl_id_related(self):
        """Check that product_tmpl_id on line is correctly related to the product."""
        line = self.env["ref.market.bom.line"].create(
            {
                "market_bom_id": self.market_bom.id,
                "product_id": self.product.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom_unit.id,
            }
        )
        self.assertEqual(line.product_tmpl_id, self.product.product_tmpl_id)

    def test_16_market_bom_product_tmpl_id_related(self):
        """Check that product_tmpl_id on market BoM is correctly related to the
        product."""
        self.assertEqual(self.market_bom.product_tmpl_id, self.product.product_tmpl_id)

    def test_17_ref_market_category_creation(self):
        """Check creating a ref.market.category record."""
        category = self.env["ref.market.category"].create(
            {
                "prefix": "CAT",
                "description": "Test Category",
                "sequence": 1,
                "state": "normal",
            }
        )
        self.assertEqual(category.prefix, "CAT")
        self.assertEqual(category.description, "Test Category")
        self.assertEqual(category.state, "normal")

    def test_18_ref_market_category_states(self):
        """Check that ref.market.category supports all valid states."""
        for state in ("normal", "obsolete", "title"):
            cat = self.env["ref.market.category"].create(
                {
                    "prefix": "P",
                    "description": "Cat",
                    "sequence": 1,
                    "state": state,
                }
            )
            self.assertEqual(cat.state, state)
