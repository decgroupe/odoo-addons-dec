# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo import Command

from .common import TestSaleDeliveryRateCommon


class TestSaleDeliveryRate(TestSaleDeliveryRateCommon):
    """Tests for sale_delivery_rate module."""

    def _confirm_sale_order(self, order):
        """Confirm a sale order and return it."""
        order.action_confirm()
        return order

    def _create_sale_order(self, lines):
        """Create and return a sale order with the given order lines."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": lines,
            }
        )
        return order

    def _create_storable_line(self, qty):
        """Return an order line command for a storable product."""
        return Command.create(
            {
                "product_id": self.storable_product.id,
                "product_uom_qty": qty,
            }
        )

    def _create_project_and_task(self, sale_line, progress=0, is_closed=False):
        """Create a project and task linked to the given sale order line."""
        project = self.env["project.project"].create({"name": "Test Project"})
        state = "1_done" if is_closed else "01_in_progress"
        task = self.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": project.id,
                "sale_line_id": sale_line.id,
                "state": state,
                "allocated_hours": 10.0 if progress > 0 else 0.0,
            }
        )
        return project, task

    def test_01_sent_rate_no_lines(self):
        """sent_rate is 100 when there are no storable product lines."""
        order = self._create_sale_order([])
        self._confirm_sale_order(order)
        self.assertEqual(order.sent_rate, 100)

    def test_02_sent_rate_zero_delivered(self):
        """sent_rate is 0 when storable lines have zero qty_delivered."""
        order = self._create_sale_order([self._create_storable_line(5)])
        self._confirm_sale_order(order)
        # no delivery done yet
        for line in order.order_line:
            line.qty_delivered = 0
        order._compute_sent_rate()
        self.assertAlmostEqual(order.sent_rate, 0.0)

    def test_03_sent_rate_partial_delivery(self):
        """sent_rate is 50 when half the storable lines are fully delivered."""
        order = self._create_sale_order(
            [
                self._create_storable_line(3),
                self._create_storable_line(2),
            ]
        )
        self._confirm_sale_order(order)
        lines = order.order_line
        lines[0].qty_delivered = 3
        lines[1].qty_delivered = 0
        order._compute_sent_rate()
        self.assertAlmostEqual(order.sent_rate, 50.0)

    def test_04_sent_rate_full_delivery(self):
        """sent_rate is 100 when all storable lines are fully delivered."""
        order = self._create_sale_order([self._create_storable_line(4)])
        self._confirm_sale_order(order)
        for line in order.order_line:
            line.qty_delivered = 4
        order._compute_sent_rate()
        self.assertAlmostEqual(order.sent_rate, 100.0)

    def test_05_delivery_rate_only_pickings(self):
        """delivery_rate equals sent_rate when there are only pickings."""
        order = self._create_sale_order([self._create_storable_line(4)])
        self._confirm_sale_order(order)
        for line in order.order_line:
            line.qty_delivered = 4
        order._compute_sent_rate()
        order._compute_delivery_rate()
        self.assertTrue(order.picking_ids)
        self.assertFalse(order.tasks_ids)
        self.assertAlmostEqual(order.delivery_rate, order.sent_rate)

    def test_06_task_rate_all_closed(self):
        """task_rate is 100 when all linked tasks are in a closed state."""
        order = self._create_sale_order(
            [
                Command.create(
                    {"product_id": self.service_product.id, "product_uom_qty": 1}
                )
            ]
        )
        self._confirm_sale_order(order)
        sale_line = order.order_line[0]
        _project, _task = self._create_project_and_task(sale_line, is_closed=True)
        order.invalidate_recordset()
        self.assertTrue(order.tasks_ids)
        order._compute_task_rate()
        self.assertAlmostEqual(order.task_rate, 100.0)

    def test_07_task_rate_no_tasks(self):
        """task_rate is 100 when there are no linked tasks."""
        order = self._create_sale_order([])
        self._confirm_sale_order(order)
        order._compute_task_rate()
        self.assertAlmostEqual(order.task_rate, 100.0)

    def test_08_delivery_rate_only_tasks(self):
        """delivery_rate equals task_rate when there are only tasks."""
        order = self._create_sale_order(
            [
                Command.create(
                    {"product_id": self.service_product.id, "product_uom_qty": 1}
                )
            ]
        )
        self._confirm_sale_order(order)
        sale_line = order.order_line[0]
        _project, _task = self._create_project_and_task(sale_line, is_closed=True)
        order.invalidate_recordset()
        self.assertFalse(order.picking_ids)
        self.assertTrue(order.tasks_ids)
        order._compute_task_rate()
        order._compute_delivery_rate()
        self.assertAlmostEqual(order.delivery_rate, order.task_rate)

    def test_09_delivery_status_none(self):
        """delivery_status is 'none' when line qty is zero."""
        order = self._create_sale_order(
            [
                Command.create(
                    {"product_id": self.storable_product.id, "product_uom_qty": 0}
                )
            ]
        )
        self._confirm_sale_order(order)
        line = order.order_line.filtered(lambda line: not line.display_type)[0]
        line.product_uom_qty = 0
        line._compute_delivery_status()
        self.assertEqual(line.delivery_status, "none")

    def test_10_delivery_status_todo(self):
        """delivery_status is 'todo' when line is only partially delivered."""
        order = self._create_sale_order([self._create_storable_line(10)])
        self._confirm_sale_order(order)
        line = order.order_line.filtered(lambda line: not line.display_type)[0]
        line.qty_delivered = 5
        line._compute_delivery_status()
        self.assertEqual(line.delivery_status, "todo")

    def test_11_delivery_status_full(self):
        """delivery_status is 'full' when line is fully delivered."""
        order = self._create_sale_order([self._create_storable_line(10)])
        self._confirm_sale_order(order)
        line = order.order_line.filtered(lambda line: not line.display_type)[0]
        line.qty_delivered = 10
        line._compute_delivery_status()
        self.assertEqual(line.delivery_status, "full")

    def test_12_list_view_fields(self):
        """Check that delivery_rate field is present in the sale order list view."""
        view_info = self.env["sale.order"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("delivery_rate", field_names)

    def test_13_form_view_fields(self):
        """Check that rate fields are present in the sale order form view."""
        view_info = self.env["sale.order"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("sent_rate", field_names)
        self.assertIn("task_rate", field_names)
        self.assertIn("tasks_ids", field_names)

    def test_14_task_rate_open_task_with_progress(self):
        """task_rate uses task.progress when the task is not closed."""
        order = self._create_sale_order(
            [
                Command.create(
                    {"product_id": self.service_product.id, "product_uom_qty": 1}
                )
            ]
        )
        self._confirm_sale_order(order)
        sale_line = order.order_line[0]
        _project, task = self._create_project_and_task(sale_line, is_closed=False)
        # force progress to 0 (no timesheets) — task is open so progress branch is hit
        task.with_context(tracking_disable=True).write({"allocated_hours": 0.0})
        order.invalidate_recordset()
        self.assertTrue(order.tasks_ids)
        order._compute_task_rate()
        # progress=0 and is_closed=False, so task_rate = 0/1 = 0
        self.assertAlmostEqual(order.task_rate, 0.0)

    def test_15_delivery_rate_pickings_and_tasks(self):
        """delivery_rate combines sent_rate and task_rate when both exist."""
        order = self._create_sale_order(
            [
                self._create_storable_line(4),
                Command.create(
                    {"product_id": self.service_product.id, "product_uom_qty": 1}
                ),
            ]
        )
        self._confirm_sale_order(order)
        storable_line = order.order_line.filtered(
            lambda line: line.product_id == self.storable_product
        )
        storable_line.qty_delivered = 4
        service_line = order.order_line.filtered(
            lambda line: line.product_id == self.service_product
        )
        _project, _task = self._create_project_and_task(service_line, is_closed=True)
        order.invalidate_recordset()
        self.assertTrue(order.picking_ids)
        self.assertTrue(order.tasks_ids)
        order._compute_sent_rate()
        order._compute_task_rate()
        order._compute_delivery_rate()
        expected = order.sent_rate + order.task_rate / 2.0
        self.assertAlmostEqual(order.delivery_rate, expected)
