# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    effective_last_date = fields.Date(
        string="Latest Effective Date",
        compute="_compute_effective_last_date",
        store=True,
        help="Completion date of the last delivery order.",
    )
    expected_last_date = fields.Datetime(
        string="Latest Expected Date",
        compute="_compute_expected_last_date",
        store=False,  # Note: can not be stored since depends on today()
        help="Latest delivery date that you can tell your customer, "
        "computed from product lead times.",
    )

    @api.depends("order_line.last_effective_date")
    def _compute_effective_last_date(self):
        for order in self:
            dates_list = order.order_line.mapped("last_effective_date")
            dates_list = [d for d in dates_list if d]  # filter out falsy values
            if not dates_list:
                order.effective_last_date = False
            else:
                order.effective_last_date = dates_list and fields.Date.context_today(
                    order, max(dates_list)
                )

    @api.depends("order_line.customer_lead", "date_order", "order_line.state")
    def _compute_expected_last_date(self):
        # Based on `SaleOrder._compute_expected_date` from `sale` module. Note that
        # this computation will give `expected_last_date == expected_last_date` when
        # `picking_policy` is `one` (Deliver only when all products are ready)
        self.mapped("order_line")  # Prefetch indication
        for order in self:
            if order.state == "cancel":
                order.expected_date = False
                continue
            dates_list = order.order_line.filtered(
                lambda line: not line.display_type and not line._is_delivery()
            ).mapped(lambda line: line and line._expected_date())
            if dates_list:
                order.expected_last_date = order._select_expected_last_date(dates_list)
            else:
                order.expected_last_date = False

    def _select_expected_last_date(self, expected_dates):
        self.ensure_one()
        return max(expected_dates)
