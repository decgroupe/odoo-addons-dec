# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import models, api, fields


def stockpicking_state_to_emoji(state):
    res = state
    if res == 'draft':
        res = '🏳️'
    elif res == 'waiting':
        res = '⛓️'
    elif res == 'confirmed':
        res = '⏳'
    elif res == 'assigned':
        res = '✳️'
    elif res == 'done':
        res = '✅'
    elif res == 'cancel':
        res = '❌'
    return res


class StockPicking(models.Model):
    _inherit = "stock.picking"

    state_emoji = fields.Char(compute='_compute_state_emoji')

    def _compute_state_emoji(self):
        for rec in self:
            rec.state_emoji = stockpicking_state_to_emoji(rec.state)

    def get_head_desc(self):
        state = dict(self._fields['state']._description_selection(self.env)
                    ).get(self.state)
        head = '🗳️{0}'.format(self.name)
        desc = '{0}{1}'.format(self.state_emoji, state)
        return head, desc
