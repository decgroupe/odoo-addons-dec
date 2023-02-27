# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

import logging

from odoo import fields, api, models

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_set_lost(self, **additional_values):
        res = super().action_set_lost(**additional_values)
        for lead in self:
            # Set lost stage when probability is set to 0
            stage_id = lead._stage_find(domain=[('probability', '<=', 0)])
            lead.write({'stage_id': stage_id.id})
        return res

    @api.model
    def _onchange_stage_id_values(self, stage_id):
        vals = super()._onchange_stage_id_values(stage_id)
        # When probability is set to 0, always set active to false, that way
        # date_closed will be set
        if 'probability' in vals and vals.get('probability') <= 0:
            vals['active'] = False
        return vals
