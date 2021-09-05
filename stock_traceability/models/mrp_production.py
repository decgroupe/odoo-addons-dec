# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import models, api, fields


def production_state_to_emoji(state):
    res = state
    if res == 'confirmed':
        res = '🏳️'
    elif res == 'planned':
        res = '📅'
    elif res == 'progress':
        res = '🚧'
    elif res == 'done':
        res = '✅'
    elif res == 'cancel':
        res = '❌'
    return res


class Production(models.Model):
    _inherit = "mrp.production"

    state_emoji = fields.Char(compute='_compute_state_emoji')

    @api.multi
    def _compute_state_emoji(self):
        for rec in self:
            rec.state_emoji = production_state_to_emoji(rec.state)

    def get_head_desc(self):
        state = dict(self._fields['state']._description_selection(self.env)
                    ).get(self.state)
        head = '⚙️{0}'.format(self.name)
        desc = '{0}{1}'.format(self.state_emoji, state)
        return head, desc
