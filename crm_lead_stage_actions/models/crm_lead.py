# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def write(self, vals):
        enforce_date_closed = False
        if vals.get("stage_id"):
            lost_stage_id = self._stage_find(domain=[("is_lost", "=", True)])
            won_stage_id = self._stage_find(domain=[("is_won", "=", True)])
            if vals.get("stage_id") == lost_stage_id.id:
                # archive
                self.action_set_lost()
                enforce_date_closed = True
            elif vals.get("stage_id") == won_stage_id.id:
                # unarchive and set an `is_won` stage
                self.action_set_won()
        return super(
            CrmLead, self.with_context(enforce_date_closed=enforce_date_closed)
        ).write(vals)

    def action_set_lost(self, **additional_values):
        if self.env.context.get("action_set"):
            return False
        else:
            lost_stage_id = self._stage_find(domain=[("is_lost", "=", True)])
            additional_values["stage_id"] = lost_stage_id.id

            res = super(CrmLead, self.with_context(action_set=True)).action_set_lost(
                **additional_values
            )
            return res

    def action_set_won(self):
        if self.env.context.get("action_set"):
            return False
        else:
            res = super(CrmLead, self.with_context(action_set=True)).action_set_won()
            return res

    def _handle_won_lost(self, vals):
        # use this handle to hook write and set the `date_closed`
        if self.env.context.get("enforce_date_closed"):
            vals["date_closed"] = fields.Datetime.now()
        return super()._handle_won_lost(vals)

    @api.model
    def _onchange_stage_id_values(self, stage_id):
        vals = super()._onchange_stage_id_values(stage_id)
        return vals
