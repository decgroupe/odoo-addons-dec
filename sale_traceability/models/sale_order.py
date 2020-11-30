# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Nov 2020

from odoo import models, api, fields


def sale_state_to_emoji(state):
    res = state
    if res == 'draft':
        res = '🏳️'
    elif res == 'sent':
        res = '📩'
    elif res == 'sale':
        res = '💲'
    elif res == 'done':
        res = '✅'
    elif res == 'cancel':
        res = '❌'
    return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state_emoji = fields.Char(compute='_compute_state_emoji')

    @api.multi
    def _compute_state_emoji(self):
        for rec in self:
            rec.state_emoji = sale_state_to_emoji(rec.state)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_head_desc(self):
        state = dict(self._fields['state']._description_selection(self.env)
                    ).get(self.state)
        head = '📈{0}'.format(self.order_id.name)
        desc = '{0}{1}'.format(self.order_id.state_emoji, state)
        return head, desc
