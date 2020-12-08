# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Dec 2020

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
    @api.depends('tasks_ids', 'tasks_ids.progress')
    def _compute_task_rate(self):
        for sale in self:
            all_task_ids = sale.tasks_ids
            if all_task_ids:
                sale.task_rate = sum(all_task_ids.mapped('progress')) \
                    / len(all_task_ids)

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
