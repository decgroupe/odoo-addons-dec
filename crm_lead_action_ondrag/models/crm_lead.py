# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

import logging

from odoo import fields, api, models

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def write(self, vals):
        if vals.get('stage_id') and not 'set_stage' in self._context:
            lost_stage_id = self._stage_find(domain=[('probability', '<=', 0)])
            won_stage_id = self._stage_find(domain=[('probability', '>=', 100)])
            if vals.get('stage_id') == lost_stage_id.id:
                self.with_context(set_stage=True).action_set_lost()
            elif vals.get('stage_id') == won_stage_id.id:
                self.with_context(set_stage=True).action_set_won()
        return super().write(vals)
