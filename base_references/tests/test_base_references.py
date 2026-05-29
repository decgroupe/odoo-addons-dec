# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from lxml import etree

from odoo.exceptions import UserError

from .common import TestBaseReferencesCommon


class TestBaseReferences(TestBaseReferencesCommon):
    """Tests for base_references module."""

    def test_01_default_get_with_ir_model_context(self):
        """default_get pre-fills model_id when opened from the ir.model form."""
        result = self.Wizard.with_context(
            active_model="ir.model",
            active_id=self.partner_ir_model.id,
        ).default_get(["model_id"])
        self.assertEqual(result.get("model_id"), self.partner_ir_model.id)

    def test_02_default_get_without_context(self):
        """default_get does not set model_id when context lacks active_model."""
        result = self.Wizard.default_get(["model_id"])
        self.assertNotIn("model_id", result)

    def test_03_compute_record_display_name_valid(self):
        """_compute_record_display_name returns the record display name."""
        wizard = self._create_wizard(self.partner_ir_model.id, self.partner_parent.id)
        self.assertEqual(wizard.record_display_name, self.partner_parent.display_name)

    def test_04_compute_record_display_name_invalid_res_id(self):
        """_compute_record_display_name returns False for a non-existent res_id."""
        wizard = self._create_wizard(self.partner_ir_model.id, 999999999)
        self.assertFalse(wizard.record_display_name)

    def test_05_search_raises_on_nonexistent_record(self):
        """action_search_references raises UserError for a non-existent record."""
        wizard = self._create_wizard(self.partner_ir_model.id, 999999999)
        with self.assertRaises(UserError):
            wizard.action_search_references()

    def test_06_search_many2one_finds_child_partner(self):
        """action_search_references finds many2one references via parent_id."""
        wizard = self._create_wizard(self.partner_ir_model.id, self.partner_parent.id)
        action = wizard.action_search_references()
        # verify action structure
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "base.references.result")
        # check that partner_child (parent_id -> partner_parent) is in results
        results = self.Result.search(action["domain"])
        m2o_results = results.filtered(
            lambda r: r.reference_type == "many2one"
            and r.model == "res.partner"
            and r.field_name == "parent_id"
        )
        self.assertIn(self.partner_child.id, m2o_results.mapped("res_id"))

    def test_07_search_many2many_finds_categorized_partner(self):
        """action_search_references finds many2many references via category_id."""
        wizard = self._create_wizard(self.category_ir_model.id, self.test_category.id)
        action = wizard.action_search_references()
        results = self.Result.search(action["domain"])
        m2m_results = results.filtered(lambda r: r.reference_type == "many2many")
        self.assertIn(self.partner_with_category.id, m2m_results.mapped("res_id"))

    def test_08_result_count_updated_after_search(self):
        """action_search_references updates result_count on the wizard."""
        wizard = self._create_wizard(self.partner_ir_model.id, self.partner_parent.id)
        wizard.action_search_references()
        self.assertGreater(wizard.result_count, 0)

    def test_09_action_open_record_returns_form_action(self):
        """action_open_record returns a form act_window for the referencing record."""
        wizard = self._create_wizard(self.partner_ir_model.id, self.partner_parent.id)
        wizard.action_search_references()
        result_line = self.Result.search([("wizard_id", "=", wizard.id)], limit=1)
        self.assertTrue(result_line)
        action = result_line.action_open_record()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], result_line.model)
        self.assertEqual(action["res_id"], result_line.res_id)
        self.assertEqual(action["view_mode"], "form")

    def test_10_is_model_searchable_transient(self):
        """_is_model_searchable returns False for transient models."""
        wizard = self._create_wizard(self.partner_ir_model.id, self.partner_parent.id)
        self.assertFalse(wizard._is_model_searchable("base.references.wizard"))

    def test_11_is_model_searchable_abstract(self):
        """_is_model_searchable returns False for abstract models."""
        wizard = self._create_wizard(self.partner_ir_model.id, self.partner_parent.id)
        # 'base' is a registered AbstractModel (ir_model.py)
        self.assertFalse(wizard._is_model_searchable("base"))

    def test_12_is_model_searchable_regular_model(self):
        """_is_model_searchable returns True for a regular stored model."""
        wizard = self._create_wizard(self.partner_ir_model.id, self.partner_parent.id)
        self.assertTrue(wizard._is_model_searchable("res.partner"))

    def test_13_is_model_searchable_unknown_model(self):
        """_is_model_searchable returns False for an unknown model name."""
        wizard = self._create_wizard(self.partner_ir_model.id, self.partner_parent.id)
        self.assertFalse(wizard._is_model_searchable("no.such.model"))

    def test_14_wizard_form_view_fields(self):
        """Wizard form view contains expected fields."""
        view_info = self.env["base.references.wizard"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("model_id", field_names)
        self.assertIn("res_id", field_names)
        self.assertIn("record_display_name", field_names)
        self.assertIn("result_count", field_names)

    def test_15_result_list_view_fields(self):
        """Result list view contains expected fields."""
        view_info = self.env["base.references.result"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("model", field_names)
        self.assertIn("res_id", field_names)
        self.assertIn("record_display_name", field_names)
        self.assertIn("field_name", field_names)
        self.assertIn("reference_type", field_names)

    def test_16_search_clears_previous_results(self):
        """Running action_search_references twice replaces the previous results."""
        wizard = self._create_wizard(self.partner_ir_model.id, self.partner_parent.id)
        # first run
        action = wizard.action_search_references()
        count_first = self.Result.search_count(action["domain"])
        # second run on the same wizard must not accumulate results
        wizard.action_search_references()
        count_second = self.Result.search_count(action["domain"])
        self.assertEqual(count_first, count_second)
