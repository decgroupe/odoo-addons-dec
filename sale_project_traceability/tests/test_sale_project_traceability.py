# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestSaleProjectTraceability(TransactionCase):
    """Tests for sale_project_traceability module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Service Product",
                "type": "service",
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
                "partner_id": cls.partner.id,
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )
        cls.sol = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order.id,
                "product_id": cls.product.id,
                "product_uom_qty": 1,
            }
        )

    def test_01_task_ids_field_exists(self):
        """The sale.order.line model has a task_ids One2many field."""
        self.assertIn("task_ids", self.env["sale.order.line"]._fields)

    def test_02_task_ids_empty_by_default(self):
        """A new sale order line has no linked tasks."""
        self.assertFalse(self.sol.task_ids)

    def test_03_task_linked_via_sale_line_id(self):
        """A task with sale_line_id set appears in sol.task_ids."""
        task = self.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": self.project.id,
                "sale_line_id": self.sol.id,
            }
        )
        self.assertIn(task, self.sol.task_ids)

    def test_04_task_unlinked_clears_task_ids(self):
        """Removing sale_line_id from a task removes it from sol.task_ids."""
        task = self.env["project.task"].create(
            {
                "name": "Test Task 2",
                "project_id": self.project.id,
                "sale_line_id": self.sol.id,
            }
        )
        self.assertIn(task, self.sol.task_ids)
        task.sale_line_id = False
        self.assertNotIn(task, self.sol.task_ids)

    def test_05_multiple_tasks_same_sol(self):
        """Multiple tasks can reference the same sale order line."""
        task1 = self.env["project.task"].create(
            {
                "name": "Task A",
                "project_id": self.project.id,
                "sale_line_id": self.sol.id,
            }
        )
        task2 = self.env["project.task"].create(
            {
                "name": "Task B",
                "project_id": self.project.id,
                "sale_line_id": self.sol.id,
            }
        )
        self.assertIn(task1, self.sol.task_ids)
        self.assertIn(task2, self.sol.task_ids)
        self.assertEqual(len(self.sol.task_ids), 2)

    def test_06_tasks_isolated_between_sol(self):
        """Tasks linked to one SOL do not appear on another SOL."""
        sol2 = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 2,
            }
        )
        task = self.env["project.task"].create(
            {
                "name": "Isolated Task",
                "project_id": self.project.id,
                "sale_line_id": self.sol.id,
            }
        )
        self.assertIn(task, self.sol.task_ids)
        self.assertNotIn(task, sol2.task_ids)
