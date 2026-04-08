# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from .common import TestProductReferenceAnalyticCommon


class TestProductReferenceAnalytic(TestProductReferenceAnalyticCommon):
    """Tests for product_reference_analytic module."""

    def _create_category(self, code, name):
        """Create a ref.category with the given code and name."""
        return self.env["ref.category"].create({"code": code, "name": name})

    def test_01_form_view_fields(self):
        """Check that expected fields are present in the combined form view arch."""
        view_info = self.env["ref.category"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("income_analytic_account_id", field_names)

    def test_02_auto_create_on_category_creation(self):
        """Creating a ref.category with auto-create enabled creates an analytic
        account."""
        self.company.auto_create_reference_category_analytic_account = True
        category = self._create_category("TST01", "Test Category 01")
        self.assertTrue(category.income_analytic_account_id)
        self.assertEqual(category.income_analytic_account_id.name, "Test Category 01")
        self.assertEqual(category.income_analytic_account_id.code, "TST01")
        self.assertEqual(
            category.income_analytic_account_id.plan_id, self.analytic_plan
        )

    def test_03_no_auto_create_when_disabled(self):
        """Creating a ref.category with auto-create disabled does not create an
        analytic account."""
        self.company.auto_create_reference_category_analytic_account = False
        category = self._create_category("TST02", "Test Category 02")
        self.assertFalse(category.income_analytic_account_id)

    def test_04_action_create_analytic_account(self):
        """Calling action_create_income_analytic_account creates accounts for
        categories without one."""
        self.company.auto_create_reference_category_analytic_account = False
        category = self._create_category("TST03", "Test Category 03")
        self.assertFalse(category.income_analytic_account_id)
        category.action_create_income_analytic_account()
        self.assertTrue(category.income_analytic_account_id)
        self.assertEqual(
            category.income_analytic_account_id.plan_id, self.analytic_plan
        )

    def test_05_action_skips_category_with_existing_account(self):
        """Calling action_create_income_analytic_account does not overwrite an
        existing account."""
        self.company.auto_create_reference_category_analytic_account = False
        category = self._create_category("TST04", "Test Category 04")
        existing_account = self.env["account.analytic.account"].create(
            {
                "name": "Existing Account",
                "plan_id": self.analytic_plan.id,
            }
        )
        category.income_analytic_account_id = existing_account
        category.action_create_income_analytic_account()
        self.assertEqual(category.income_analytic_account_id, existing_account)

    def test_06_write_name_sync(self):
        """Renaming a ref.category updates the linked analytic account name."""
        self.company.auto_create_reference_category_analytic_account = True
        category = self._create_category("TST05", "Test Category 05")
        self.assertTrue(category.income_analytic_account_id)
        # rename the category — the analytic account name should sync
        category.write({"name": "Test Category 05 Renamed"})
        self.assertEqual(
            category.income_analytic_account_id.name, "Test Category 05 Renamed"
        )

    def test_07_write_name_no_sync_when_names_differ(self):
        """Renaming a ref.category does not sync if analytic account name was
        already changed."""
        self.company.auto_create_reference_category_analytic_account = True
        category = self._create_category("TST06", "Test Category 06")
        # manually change the analytic account name so it no longer matches
        category.income_analytic_account_id.name = "Custom Analytic Name"
        category.write({"name": "Test Category 06 Renamed"})
        # name should NOT be synced since analytic name != old category name
        self.assertEqual(
            category.income_analytic_account_id.name, "Custom Analytic Name"
        )

    def test_08_write_code_sync(self):
        """Changing a ref.category code updates the linked analytic account code."""
        self.company.auto_create_reference_category_analytic_account = True
        category = self._create_category("TST07", "Test Category 07")
        self.assertTrue(category.income_analytic_account_id)
        # change the code — the analytic account code should sync
        category.write({"code": "TST07NEW"})
        self.assertEqual(category.income_analytic_account_id.code, "TST07NEW")

    def test_09_write_code_no_sync_when_codes_differ(self):
        """Changing a ref.category code does not sync if analytic account code
        was already changed."""
        self.company.auto_create_reference_category_analytic_account = True
        category = self._create_category("TST08", "Test Category 08")
        # manually change the analytic account code so it no longer matches
        category.income_analytic_account_id.code = "CUSTOM_CODE"
        category.write({"code": "TST08NEW"})
        # code should NOT be synced since analytic code != old category code
        self.assertEqual(category.income_analytic_account_id.code, "CUSTOM_CODE")

    def test_10_res_config_settings_field(self):
        """The auto-create setting is accessible via res.config.settings."""
        settings = self.env["res.config.settings"].create({})
        self.company.auto_create_reference_category_analytic_account = True
        self.assertTrue(settings.auto_create_reference_category_analytic_account)
        self.company.auto_create_reference_category_analytic_account = False
        settings.invalidate_recordset()
        self.assertFalse(settings.auto_create_reference_category_analytic_account)
