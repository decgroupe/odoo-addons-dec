# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import models, api, fields


def production_request_state_to_emoji(state):
    res = state
    if res == 'draft':
        res = '🏳️'
    elif res == 'to_approve':
        res = '⏳'
    elif res == 'approved':
        res = '🚧'
    elif res == 'done':
        res = '✅'
    elif res == 'cancel':
        res = '❌'
    return res


class ProductionRequest(models.Model):
    _inherit = "mrp.production.request"

    state_emoji = fields.Char(compute='_compute_state_emoji')

    def _compute_state_emoji(self):
        for rec in self:
            rec.state_emoji = production_request_state_to_emoji(rec.state)

    def get_head_desc(self):
        p = self.sudo()
        state = dict(p._fields['state']._description_selection(self.env)).get(
            p.state
        )
        head = '⚙️{0}'.format(p.name)
        desc = '{0}{1}'.format(p.state_emoji, state)
        return head, desc
