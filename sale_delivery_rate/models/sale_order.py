# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sent_rate = fields.Float(
        compute="_compute_sent_rate",
        help="Rate of sent products",
    )
    task_rate = fields.Float(
        compute="_compute_task_rate",
        help="Rate of tasks progression",
    )
    delivery_rate = fields.Float(
        compute="_compute_delivery_rate",
        help="Rate of delivery",
    )

    @api.depends("state", "order_line.qty_delivered", "order_line.product_uom_qty")
    def _compute_sent_rate(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        self.sent_rate = 100
        for sale in self:
            sent_count = 0
            line_count = 0
            for line in sale.order_line:
                if (
                    line.product_id.type in ("consu", "product")
                    and line.product_uom_qty > 0
                ):
                    line_count += 1
                    if (
                        float_compare(
                            line.qty_delivered,
                            line.product_uom_qty,
                            precision_digits=precision,
                        )
                        >= 0
                    ):
                        sent_count += 1
            if line_count > 0:
                sale.sent_rate = sent_count * 100 / line_count

    @api.depends("tasks_ids", "tasks_ids.progress", "tasks_ids.stage_id")
    def _compute_task_rate(self):
        self.task_rate = 100
        for sale in self:
            all_task_ids = sale.tasks_ids
            total_progress = 0
            if all_task_ids:
                for task_id in all_task_ids:
                    # If the task stage is cancel or done, consider its
                    # progress as 100%
                    if task_id.stage_id.is_closed:
                        total_progress += 100
                    else:
                        total_progress += task_id.progress
                sale.task_rate = total_progress / len(all_task_ids)

    @api.depends("sent_rate", "task_rate")
    def _compute_delivery_rate(self):
        self.delivery_rate = 100
        for sale in self:
            if sale.picking_ids and sale.tasks_ids:
                sale.delivery_rate = sale.sent_rate + sale.task_rate / 2.0
            elif sale.picking_ids:
                sale.delivery_rate = sale.sent_rate
            elif sale.tasks_ids:
                sale.delivery_rate = sale.task_rate
