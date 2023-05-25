# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.onchange("lead_id")
    def _onchange_lead_id(self):
        if not self.lead_id:
            return
        # If the currently assigned project is not the lead one
        # or if this project is not linked to the lead the unset it
        if self.project_id not in (
            self.lead_id.project_id + self.lead_id.related_project_ids
        ):
            self.project_id = False
        if not self.project_id and self.lead_id.project_id:
            super()._onchange_lead_id()

    @api.onchange("project_id")
    def _onchange_project_id(self):
        res = super()._onchange_project_id()
        if "domain" in res:
            filter = []
            if self.project_id:
                filter = [
                    "|",
                    ("project_id", "=", self.project_id.id),
                    ("related_project_ids", "=", self.project_id.id),
                ]
            res["domain"]["lead_id"] = filter
        # Automatically select the linked opportunity
        if not self.lead_id and self.project_id.linked_lead_id:
            self.lead_id = self.project_id.linked_lead_id
        return res
