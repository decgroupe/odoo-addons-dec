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
