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

    def _compute_state_emoji(self):
        for rec in self:
            rec.state_emoji = production_state_to_emoji(rec.state)

    def get_head_desc(self):
        # Soft dependency to `mrp_stage` module
        if hasattr(self, 'stage_id'):
            state = self.stage_id.name
            code = self.stage_id.code
            emoji = self.stage_id.emoji
        else:
            state = dict(
                self._fields['state']._description_selection(self.env)
            ).get(self.state)
            code = self.state
            emoji = self.state_emoji

        # Soft dependency to `mrp_timesheet` module
        if hasattr(self, 'progress') and code == 'progress':
            state = "{0} {1:.0f}%".format(state, self.progress)
        # Soft dependency to `mrp_supply_progress` module
        elif hasattr(self, 'supply_progress') and code == 'supplying':
            state = "{0} {1:.0f}%".format(state, self.supply_progress)

        head = '🔧{0}'.format(self.name)
        desc = '{0}{1}'.format(emoji, state)
        return head, desc
