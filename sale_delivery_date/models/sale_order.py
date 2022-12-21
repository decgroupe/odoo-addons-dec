# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from datetime import datetime, timedelta

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    effective_last_date = fields.Date(
        string="Latest Effective Date",
        compute='_compute_effective_last_date',
        store=True,
        help="Completion date of the last delivery order."
    )

    expected_last_date = fields.Datetime(
        string="Latest Expected Date",
        compute='_compute_expected_last_date',
        store=False,  # Note: can not be stored since depends on today()
        help="Latest delivery date that you can tell your customer, "
        "computed from product lead times."
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

    @api.depends(
        'order_line.customer_lead', 'date_order', 'order_line.state'
    )
    def _compute_expected_last_date(self):
        for order in self:
            dates_list = []
            confirm_date = fields.Datetime.from_string(
                (order.date_order or order.write_date
                ) if order.state in ('sale', 'done') else fields.Datetime.now()
            )
            for line in order.order_line.filtered(
                lambda x: x.state != 'cancel' and not x._is_delivery()
            ):
                dt = confirm_date + timedelta(days=line.customer_lead or 0.0)
                dates_list.append(dt)
            if dates_list:
                expected_date = max(dates_list)
                order.expected_last_date = fields.Datetime.to_string(
                    expected_date
                )
            else:
                order.expected_last_date = False

