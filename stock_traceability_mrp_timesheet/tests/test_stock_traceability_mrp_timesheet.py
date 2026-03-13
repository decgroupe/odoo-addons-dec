# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import logging

from .common import TestStockTraceabilityMrpTimesheetBase

_logger = logging.getLogger(__name__)


class TestStockTraceabilityMrpTimesheet(TestStockTraceabilityMrpTimesheetBase):
    """Tests for Stock Traceability module."""

    def test_01_production_head_description(self):
        production = self.env["mrp.production"].create(
            {
                "name": "WH/MO/TEST/01/01",
                "product_id": self.manufacturable_product.id,
                "product_uom_id": self.manufacturable_product.uom_id.id,
                "product_qty": 1,
            }
        )
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "✨Draft")
        # change state to confirmed
        production.action_confirm()
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "🏳️Confirmed")
        # enforce "progress" state
        production.action_start()
        self.assertEqual(production.stage_id.code, "progress")
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "🚧In Progress 0%")
        # add support for timesheet to the production
        production.action_create_project()
        production.planned_hours = 4
        self.assertTrue(production.project_id)
        # create a first timesheet entry for this production
        _al1 = self.env["account.analytic.line"].create(
            {
                "name": "Picking products from stock",
                "project_id": production.project_id.id,
                "production_id": production.id,
                "employee_id": self.production_employee.id,
                "unit_amount": 1,  # one hour
                "date": production.date_start,
            }
        )
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "🚧In Progress 25%")
        # change stage code, progress should be missing
        production.stage_id.code = "Tututu"
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "🚧In Progress")
        production.stage_id.code = "progress"
        # add a second timesheet entry for this production
        _al2 = self.env["account.analytic.line"].create(
            {
                "name": "Assembling the product",
                "project_id": production.project_id.id,
                "production_id": production.id,
                "employee_id": self.production_employee.id,
                "unit_amount": 2,  # two hours
                "date": production.date_start,
            }
        )
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "🚧In Progress 75%")
        # add a last timesheet entry (with an extra time) for this production
        _al3 = self.env["account.analytic.line"].create(
            {
                "name": "Fixing assembling",
                "project_id": production.project_id.id,
                "production_id": production.id,
                "employee_id": self.production_employee.id,
                "unit_amount": 3,  # three hours
                "date": production.date_start,
            }
        )
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "🚧In Progress 100%")
