# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    effective_last_date = fields.Date(
        "Effective Last Date",
        compute='_compute_effective_last_date',
        store=True,
        help="Completion date of the last delivery order."
    )

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
