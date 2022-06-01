# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sent_rate = fields.Float(
        compute='_compute_sent_rate',
        help='Rate of sent products',
    )
    task_rate = fields.Float(
        compute='_compute_task_rate',
        help='Rate of tasks progression',
    )
    delivery_rate = fields.Float(
        compute='_compute_delivery_rate',
        help='Rate of delivery',
    )
    effective_last_date = fields.Date(
        "Effective Last Date",
        compute='_compute_effective_last_date',
        store=True,
        help="Completion date of the last delivery order."
    )

    @api.multi
    @api.depends(
        'picking_ids', 'picking_ids.move_lines', 'picking_ids.move_lines.state'
    )
    def _compute_sent_rate(self):
        for sale in self:
            all_move_ids = sale.picking_ids.mapped('move_lines').filtered(
                lambda x: x.state != 'cancel'
            )
            if all_move_ids:
                received_move_ids = all_move_ids.filtered(
                    lambda x: x.state == 'done'
                )
                sale.sent_rate = \
                    len(received_move_ids) * 100 / len(all_move_ids)

    @api.multi
    @api.depends('tasks_ids', 'tasks_ids.progress', 'tasks_ids.stage_id')
    def _compute_task_rate(self):
        for sale in self:
            all_task_ids = sale.tasks_ids
            total_progress = 0
            if all_task_ids:
                for task_id in all_task_ids:
                    # If the task stage is cancel or done, consider its
                    # progress as 100%
                    if task_id.stage_id.fold:
                        total_progress += 100
                    else:
                        total_progress += task_id.progress
                sale.task_rate = total_progress / len(all_task_ids)

    @api.multi
    @api.depends('sent_rate', 'task_rate')
    def _compute_delivery_rate(self):
        for sale in self:
            if sale.picking_ids and sale.tasks_ids:
                sale.delivery_rate = sale.sent_rate + sale.task_rate / 2.0
            elif sale.picking_ids:
                sale.delivery_rate = sale.sent_rate
            elif sale.tasks_ids:
                sale.delivery_rate = sale.task_rate

    @api.depends('picking_ids.date_done')
    def _compute_effective_last_date(self):
        for order in self:
            pickings = order.picking_ids.filtered(
                lambda x: x.state == 'done' and x.location_dest_id.usage ==
                'customer'
            )
            dates_list = [date for date in pickings.mapped('date_done') if date]
            order.effective_last_date = dates_list and fields.Date.context_today(
                order, max(dates_list)
            )
