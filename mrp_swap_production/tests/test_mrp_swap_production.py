# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from unittest.mock import Mock, call, patch

from lxml import etree

from odoo.exceptions import UserError

from .common import FakeSwapObject, TestMrpSwapProductionCommon


class TestMrpSwapProduction(TestMrpSwapProductionCommon):
    """Tests for mrp_swap_production module."""

    def test_01_default_get_uses_active_production(self):
        """The wizard defaults the source production from active_id."""
        production = self._create_production()
        defaults = self.WizardModel.with_context(active_id=production.id).default_get(
            ["this_production_id"]
        )
        self.assertEqual(defaults["this_production_id"], production.id)

    def test_02_onchange_creates_main_swap_line(self):
        """Changing the target production creates the main swap line."""
        wizard = self._create_wizard()
        wizard.onchange_other_production_id()
        self.assertEqual(len(wizard.swap_line_ids), 1)
        line = wizard.swap_line_ids
        self.assertEqual(line.product_id, wizard.product_id)
        self.assertEqual(line.from_production_id, wizard.this_production_id)
        self.assertEqual(line.to_production_id, wizard.other_production_id)
        self.assertTrue(line.swap_final_moves)

    def test_03_request_linkage_requires_both_orders_to_match(self):
        """Swapping requests is rejected when only one production has a request."""
        wizard = self._create_wizard()
        request = self._create_request()
        with self.assertRaisesRegex(UserError, "Both production orders"):
            wizard._pre_swap_production_request_check(request, False)
        wizard._pre_swap_production_request_check(False, False)

    def test_04_request_quantities_must_match(self):
        """Linked production requests must keep identical key fields."""
        wizard = self._create_wizard()
        request_a = self._create_request(qty=1.0)
        request_b = self._create_request(qty=2.0)
        with self.assertRaisesRegex(UserError, "product_qty"):
            wizard.swap_production_request_content(request_a, request_b, False)

    def test_05_message_post_swap_notifies_both_records(self):
        """Posting swap messages targets both records with a linked body."""
        wizard = self._create_wizard()
        first = Mock(_name="mrp.production", id=11, name="MO-11")
        second = Mock(_name="mrp.production", id=12, name="MO-12")
        wizard.message_post_swap(first, second)
        first.message_post.assert_called_once()
        second.message_post.assert_called_once()
        self.assertIn("Swapped with", first.message_post.call_args.kwargs["body"])
        self.assertIn("MO-12", first.message_post.call_args.kwargs["body"])
        self.assertIn("MO-11", second.message_post.call_args.kwargs["body"])

    def test_06_swap_production_calls_expected_helpers(self):
        """Swapping productions delegates each field move to helper methods."""
        wizard = self._create_wizard()
        request_a = Mock(name="request_a")
        request_b = Mock(name="request_b")
        move_finished_a = Mock(name="move_finished_a")
        move_finished_b = Mock(name="move_finished_b")
        production_a = Mock(
            display_name="MO-A",
            move_finished_ids=move_finished_a,
            mrp_production_request_id=request_a,
        )
        production_b = Mock(
            display_name="MO-B",
            move_finished_ids=move_finished_b,
            mrp_production_request_id=request_b,
        )
        production_a.with_context.return_value = production_a
        production_b.with_context.return_value = production_b
        with patch.object(type(wizard), "swap_fields", autospec=True) as swap_fields:
            with patch.object(
                type(wizard),
                "swap_production_request_content",
                autospec=True,
            ) as swap_request:
                with patch.object(
                    type(wizard), "update_timesheet_project", autospec=True
                ) as update_timesheet:
                    with patch.object(
                        type(wizard), "message_post_swap", autospec=True
                    ) as message_post:
                        wizard.swap_production(
                            production_a,
                            production_b,
                            swap_final_moves=True,
                        )
        self.assertEqual(swap_fields.call_count, 8)
        swap_fields.assert_has_calls(
            [
                call(wizard, "origin", production_a, production_b),
                call(wizard, "sale_order_id", production_a, production_b),
                call(wizard, "partner_id", production_a, production_b),
                call(wizard, "date_planned_start", production_a, production_b),
                call(wizard, "date_planned_finished", production_a, production_b),
                call(wizard, "note", production_a, production_b),
                call(wizard, "project_id", production_a, production_b),
                call(wizard, "move_dest_ids", move_finished_a, move_finished_b),
            ]
        )
        swap_request.assert_called_once_with(wizard, request_a, request_b, True)
        update_timesheet.assert_has_calls(
            [call(wizard, production_a), call(wizard, production_b)]
        )
        message_post.assert_called_once_with(wizard, production_a, production_b)

    def test_07_do_swap_validates_each_line_before_swapping(self):
        """The wizard validates all lines before executing any swap."""
        first = self._create_production()
        second = self._create_production()
        third = self._create_production()
        wizard = self._create_wizard(first, second)
        self._attach_lines(
            wizard,
            [(first, second, True), (second, third, False)],
        )
        with patch.object(
            type(wizard), "_pre_swap_production_check", autospec=True
        ) as pre_check:
            with patch.object(type(wizard), "swap_production", autospec=True) as swap:
                wizard.do_swap()
        pre_check.assert_has_calls(
            [call(wizard, first, second), call(wizard, second, third)]
        )
        swap.assert_has_calls(
            [call(wizard, first, second, True), call(wizard, second, third, False)]
        )

    def test_08_form_view_fields(self):
        """The wizard form view exposes the expected swap fields."""
        view_info = self.WizardModel.get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [element.get("name") for element in arch.iter("field")]
        self.assertIn("product_id", field_names)
        self.assertIn("this_production_id", field_names)
        self.assertIn("other_production_id", field_names)
        self.assertIn("swap_line_ids", field_names)

    def test_09_list_view_fields(self):
        """The swap line list view exposes the expected columns."""
        view = self.env.ref("mrp_swap_production.mrp_swap_production_line_tree_view")
        view_info = self.WizardLineModel.get_view(view_id=view.id, view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [element.get("name") for element in arch.iter("field")]
        self.assertEqual(arch.tag, "list")
        self.assertIn("product_id", field_names)
        self.assertIn("from_production_id", field_names)
        self.assertIn("to_production_id", field_names)
        self.assertIn("swap_final_moves", field_names)

    def test_10_identical_field_config_is_exposed(self):
        """The wizard advertises the fields that must stay identical."""
        wizard = self._create_wizard()
        field_map = wizard._get_fields_that_must_be_identical()
        self.assertEqual(
            field_map["mrp.production"],
            ["product_id", "product_qty", "product_uom_id", "allow_timesheets"],
        )
        self.assertEqual(
            field_map["mrp.production.request"],
            ["product_qty", "product_uom_id"],
        )

    def test_11_log_field_and_swap_fields_handle_recordsets_and_values(self):
        """Field logging and swapping work for recordsets, empty values and scalars."""
        wizard = self._create_wizard()
        with patch(
            "odoo.addons.mrp_swap_production.wizard.mrp_swap_production._logger_print"
        ) as logger_print:
            wizard.log_field("partner", {"partner": self.partner})
            wizard.log_field("empty", {"empty": False})
        self.assertGreaterEqual(logger_print.call_count, 3)
        first = {"value": "A"}
        second = {"value": "B"}
        wizard.swap_fields("value", first, second)
        self.assertEqual(first["value"], "B")
        self.assertEqual(second["value"], "A")
        same_left = {"value": "X"}
        same_right = {"value": "X"}
        wizard.swap_fields("value", same_left, same_right)
        self.assertEqual(same_left["value"], "X")
        self.assertEqual(same_right["value"], "X")

    def test_12_pre_swap_production_check_validates_and_calls_helpers(self):
        """Production pre-check enforces identical keys before delegating checks."""
        wizard = self._create_wizard()
        request_a = Mock(name="request_a")
        request_b = Mock(name="request_b")
        production_a = FakeSwapObject(
            {
                "product_id": 1,
                "product_qty": 2,
                "product_uom_id": 3,
                "allow_timesheets": True,
            },
            display_name="MO-A",
            mrp_production_request_id=request_a,
        )
        production_b = FakeSwapObject(
            {
                "product_id": 1,
                "product_qty": 2,
                "product_uom_id": 3,
                "allow_timesheets": True,
            },
            display_name="MO-B",
            mrp_production_request_id=request_b,
        )
        with patch.object(
            type(wizard), "_pre_swap_production_request_check", autospec=True
        ) as request_check:
            with patch.object(
                type(wizard), "_check_allowed_timesheet_swap", autospec=True
            ) as timesheet_check:
                wizard._pre_swap_production_check(production_a, production_b)
        request_check.assert_called_once_with(wizard, request_a, request_b)
        timesheet_check.assert_has_calls(
            [
                call(wizard, production_a, production_b),
                call(wizard, production_b, production_a),
            ]
        )
        production_b["product_qty"] = 99
        with self.assertRaisesRegex(UserError, "product_qty"):
            wizard._pre_swap_production_check(production_a, production_b)

    def test_13_timesheet_swap_rejects_invalid_project_configurations(self):
        """Timesheet swap guards reject each invalid project setup."""
        wizard = self._create_wizard()
        no_project = FakeSwapObject(
            {},
            timesheet_ids=[1],
            project_id=False,
            allow_timesheets=True,
            display_name="MO-A",
        )
        other = FakeSwapObject({}, project_id=True, display_name="MO-B")
        with self.assertRaisesRegex(UserError, "must have a project"):
            wizard._check_allowed_timesheet_swap(no_project, other)
        disallowed = FakeSwapObject(
            {},
            timesheet_ids=[1],
            project_id=Mock(id=10),
            allow_timesheets=False,
            display_name="MO-C",
        )
        with self.assertRaisesRegex(UserError, "allow_timesheets"):
            wizard._check_allowed_timesheet_swap(disallowed, other)
        other_without_project = FakeSwapObject(
            {}, project_id=False, display_name="MO-D"
        )
        valid_source = FakeSwapObject(
            {},
            timesheet_ids=[1],
            project_id=Mock(id=11),
            allow_timesheets=True,
            display_name="MO-E",
        )
        with self.assertRaisesRegex(UserError, "MO-D"):
            wizard._check_allowed_timesheet_swap(valid_source, other_without_project)

    def test_14_update_timesheet_project_propagates_project(self):
        """Updating timesheets writes the production project on tasks and lines."""
        wizard = self._create_wizard()
        task_ids = Mock()
        timesheet_ids = Mock()
        timesheet_ids.mapped.return_value = task_ids
        production = Mock(display_name="MO-TS")
        production.project_id = Mock(id=42)
        production.timesheet_ids = timesheet_ids
        wizard.update_timesheet_project(production)
        timesheet_ids.mapped.assert_called_once_with("task_id")
        task_ids.write.assert_called_once_with({"project_id": 42})
        timesheet_ids.write.assert_called_once_with({"project_id": 42})

    def test_15_request_content_handles_empty_requests_and_final_moves(self):
        """Request content swap short-circuits empty input and swaps final moves."""
        wizard = self._create_wizard()
        wizard.swap_production_request_content(False, False, False)
        request_a = FakeSwapObject(
            {"product_qty": 1.0, "product_uom_id": 1},
            display_name="REQ-A",
            id=10,
        )
        request_b = FakeSwapObject(
            {"product_qty": 1.0, "product_uom_id": 1},
            display_name="REQ-B",
            id=20,
        )
        move_a = Mock(name="move_a")
        move_b = Mock(name="move_b")
        with patch.object(
            type(self.env["stock.move"]), "search", autospec=True
        ) as search:
            with patch.object(
                type(wizard), "swap_fields", autospec=True
            ) as swap_fields:
                with patch.object(
                    type(wizard), "message_post_swap", autospec=True
                ) as message_post:
                    search.side_effect = [move_a, move_b]
                    wizard.swap_production_request_content(request_a, request_b, True)
        swap_fields.assert_has_calls(
            [
                call(wizard, "sale_order_id", request_a, request_b),
                call(wizard, "partner_id", request_a, request_b),
                call(wizard, "description", request_a, request_b),
                call(wizard, "origin", request_a, request_b),
                call(wizard, "date_planned_start", request_a, request_b),
                call(wizard, "date_planned_finished", request_a, request_b),
                call(wizard, "created_mrp_production_request_id", move_a, move_b),
            ]
        )
        self.assertEqual(search.call_count, 2)
        message_post.assert_called_once_with(wizard, request_a, request_b)
