# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    lead_id = fields.Many2one(
        domain="lead_id_domain",
    )
    lead_id_domain = fields.Binary(
        string="Lead/Opportunity Domain",
        help="Dynamic domain used for the `lead_id` field",
        compute="_compute_lead_id_domain",
    )

    @api.onchange("lead_id")
    def _onchange_lead_id(self):
        # if the currently assigned project is not the one (direct or related) of the
        # lead then unset it
        if self.lead_id and self.project_id not in (
            self.lead_id.project_id + self.lead_id.related_project_ids
        ):
            self.project_id = False
        # only set the project if not already set to avoid overwriting an existing
        # project when changing the lead.
        if not self.project_id:
            return super()._onchange_lead_id()
        return

    @api.onchange("project_id")
    def _onchange_project_id(self):
        res = super()._onchange_project_id()
        # Automatically select the linked opportunity
        if not self.lead_id and self.project_id.linked_lead_id:
            self.lead_id = self.project_id.linked_lead_id
        return res

    @api.depends("project_id")
    def _compute_lead_id_domain(self):
        for rec in self:
            domain = []
            if rec.project_id:
                domain = [
                    "|",
                    ("project_id", "=", rec.project_id.id),
                    ("related_project_ids", "=", rec.project_id.id),
                ]
            rec.lead_id_domain = domain
