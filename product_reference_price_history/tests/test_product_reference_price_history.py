# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from datetime import date, timedelta

from lxml import etree

from .common import TestProductReferencePriceHistoryCommon


class TestProductReferencePriceHistory(TestProductReferencePriceHistoryCommon):
    """Tests for product_reference_price_history module."""

    def test_01_display_name(self):
        """Check that ref.price display name is an empty string."""
        price = self.RefPrice.create(
            {
                "reference_id": self.reference.id,
                "value": 50.0,
                "product_count": 1,
            }
        )
        self.assertEqual(price.display_name, "")

    def test_02_price_range(self):
        """Check that _get_price_from_range returns the correct
        price for a date range."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        # create two prices on different dates
        price_old = self.RefPrice.create(
            {
                "reference_id": self.reference.id,
                "date": yesterday,
                "value": 40.0,
            }
        )
        price_new = self.RefPrice.create(
            {
                "reference_id": self.reference.id,
                "date": today,
                "value": 60.0,
            }
        )
        # search with upper bound set to today (should return the most recent <= today)
        result = self.reference._get_price_from_range(date_before=today)
        self.assertEqual(result.id, price_new.id)
        # search with upper bound set to yesterday (should return yesterday's price)
        result_old = self.reference._get_price_from_range(date_before=yesterday)
        self.assertEqual(result_old.id, price_old.id)
        # search with lower bound set to today (only today's price qualifies)
        result_today = self.reference._get_price_from_range(date_after=today)
        self.assertEqual(result_today.id, price_new.id)

    def test_03_last_prices(self):
        """Check that _get_last_prices returns the two most recent prices."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)
        self.RefPrice.create(
            {"reference_id": self.reference.id, "date": two_days_ago, "value": 30.0}
        )
        price_yesterday = self.RefPrice.create(
            {"reference_id": self.reference.id, "date": yesterday, "value": 40.0}
        )
        price_today = self.RefPrice.create(
            {"reference_id": self.reference.id, "date": today, "value": 50.0}
        )
        prices = self.reference._get_last_prices()
        self.assertEqual(len(prices), 2)
        self.assertIn(price_today.id, prices.ids)
        self.assertIn(price_yesterday.id, prices.ids)

    def test_04_scheduler_creates_price(self):
        """Check that the scheduler creates a ref.price when BOM cost has changed."""
        # no prices exist yet
        self.assertFalse(
            self.RefPrice.search([("reference_id", "=", self.reference.id)])
        )
        self.reference.run_material_cost_scheduler()
        prices = self.RefPrice.search([("reference_id", "=", self.reference.id)])
        self.assertTrue(prices)
        # cost_price of the BOM = standard_price of component × qty = 50.0 × 1 = 50.0
        self.assertEqual(round(prices[0].value, 2), 50.0)
        self.assertEqual(prices[0].product_count, 1)

    def test_05_scheduler_no_duplicate_when_unchanged(self):
        """Check that the scheduler does not create a new price if cost is unchanged."""
        # pre-seed a price matching the current BOM cost
        self.RefPrice.create(
            {
                "reference_id": self.reference.id,
                "value": 50.0,
                "product_count": 1,
            }
        )
        self.reference.run_material_cost_scheduler()
        prices = self.RefPrice.search([("reference_id", "=", self.reference.id)])
        # still only one price record - no duplicate was created
        self.assertEqual(len(prices), 1)

    def test_06_form_view_fields(self):
        """Check that price_ids field is present in the combined
        ref.reference form view."""
        view_info = self.env["ref.reference"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("price_ids", field_names)

    def test_07_scheduler_empty_recordset(self):
        """Check that the scheduler fetches all refs when called
        on an empty recordset."""
        # call on the model class (empty recordset) to trigger the
        # 'if not self.ids' branch
        self.env["ref.reference"].run_material_cost_scheduler()
        prices = self.RefPrice.search([("reference_id", "=", self.reference.id)])
        self.assertTrue(prices)

    def test_08_adt_category_skip_in_scheduler(self):
        """Check that references with ADT category are skipped by the scheduler."""
        adt_component = self.env["product.product"].create(
            {"name": "ADT Component", "standard_price": 10.0}
        )
        adt_reference = self.RefReference.create(
            {
                "category_id": self.adt_category.id,
                "product_variant_id": adt_component.id,
                "value": "ADT-001",
                "searchvalue": "ADT001",
            }
        )
        adt_reference.run_material_cost_scheduler()
        prices = self.RefPrice.search([("reference_id", "=", adt_reference.id)])
        # no price must be created for an ADT reference
        self.assertFalse(prices)

    def test_09_wizard_compute_material_cost(self):
        """Check that the compute material cost wizard calls the scheduler."""
        wizard = self.env["reference.compute_material_cost"].create({})
        # pre_execute is a no-op pass; calling it covers that branch
        wizard.pre_execute()
        # execute triggers the scheduler for all references
        wizard.execute()
        prices = self.RefPrice.search([("reference_id", "=", self.reference.id)])
        self.assertTrue(prices)

    def _create_price_increase(self):
        """Helper: seed two prices for self.reference showing a cost increase."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        self.RefPrice.create(
            {
                "reference_id": self.reference.id,
                "date": yesterday,
                "value": 30.0,
                "product_count": 1,
            }
        )
        self.RefPrice.create(
            {
                "reference_id": self.reference.id,
                "date": today,
                "value": 50.0,
                "product_count": 1,
            }
        )

    def test_10_generate_report_with_price_increase(self):
        """Check report generation when a reference has a price increase today."""
        # add an ADT reference so the ADT-skip branch (line 157) is also covered
        adt_component = self.env["product.product"].create(
            {"name": "ADT Comp Report", "standard_price": 5.0}
        )
        self.RefReference.create(
            {
                "category_id": self.adt_category.id,
                "product_variant_id": adt_component.id,
                "value": "ADT-RPT",
                "searchvalue": "ADTRPT",
            }
        )
        self._create_price_increase()
        with self.mock_smtp_send():
            self.env["ref.reference"].with_context(
                ignore_date=True
            ).generate_material_cost_report(email_to="test@example.com")

    def test_11_generate_report_with_date_range(self):
        """Check report generation with an explicit date range
        covers the date-range path."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        # price in the range [date_after, date_before]: set to today
        self.RefPrice.create(
            {
                "reference_id": self.reference.id,
                "date": today,
                "value": 50.0,
                "product_count": 1,
            }
        )
        # baseline price before date_after: set to yesterday (date <= date_after)
        self.RefPrice.create(
            {
                "reference_id": self.reference.id,
                "date": yesterday,
                "value": 30.0,
                "product_count": 1,
            }
        )
        # date_after (lower bound) = yesterday, date_before (upper bound) = tomorrow
        tomorrow = today + timedelta(days=1)
        with self.mock_smtp_send():
            self.env["ref.reference"].generate_material_cost_report(
                date_before=tomorrow,
                date_after=yesterday,
                email_to="test@example.com",
            )

    def test_12_wizard_report_default_email_and_execute(self):
        """Check that the report wizard builds default email and can run execute."""
        self._create_price_increase()
        wizard = self.env["reference.generate_material_cost_report"].create({})
        # _get_default_email_to is called on wizard creation; email_to must be set
        self.assertIsNotNone(wizard.email_to)
        # pre_execute without dates is a no-op (no assertion raised)
        wizard.pre_execute()
        # execute calls generate_material_cost_report; mock SMTP to avoid real sending
        with self.mock_smtp_send():
            wizard.write({"email_to": "test@example.com"})
            wizard.execute()

    def test_13_wizard_report_pre_execute_date_assertion(self):
        """Check that wizard pre_execute validates that date_after
        is before date_before."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        wizard = self.env["reference.generate_material_cost_report"].create(
            {
                "date_before": today,
                "date_after": yesterday,
                "use_custom_date_range": True,
            }
        )
        # date_after (yesterday) < date_before (today): assertion must pass silently
        wizard.pre_execute()
