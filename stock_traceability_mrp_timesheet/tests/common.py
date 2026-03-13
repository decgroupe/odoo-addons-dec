# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import logging

from odoo.tests import new_test_user

from odoo.addons.stock_traceability_mrp.tests.common import TestStockTraceabilityMrpBase

_logger = logging.getLogger(__name__)


class TestStockTraceabilityMrpTimesheetBase(TestStockTraceabilityMrpBase):
    """Tests for Stock Traceability module."""

    def setUp(self):
        super().setUp()
        self.production_model = self.env["mrp.production"]
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.production_user = new_test_user(
            self.env,
            login="stock_traceability_mrp_timesheet",
            groups="mrp.group_mrp_user",
            context=ctx,
        )
        self.production_user.action_create_employee()
        self.production_employee = self.production_user.employee_id
