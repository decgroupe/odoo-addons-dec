# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2024

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_task_prepare_values(self, project):
        values = super()._timesheet_create_task_prepare_values(project)
        # when task is created from sale order, it should NEVER be excluded
        values.update({"exclude_from_sale_order": False})
        return values

    def _timesheet_create_project(self):
        """Since Odoo 18.0, a new project a created from sale order line even when a
        project is already linked to the sale order. To keep the previous behaviour, we
        override this method to force the use of the existing project linked to the sale
        order.

        Note that a context key `project_account_id` is sent by the parent method to
        define the analytic account to use for the created project. This is not needed
        here since the project is already existing.
        """
        self.ensure_one()
        project = False
        if self.product_id.service_tracking == "task_in_project":
            if self.order_id.project_id:
                project = self.order_id.project_id
        if not project:
            project = super()._timesheet_create_project()
        return project
