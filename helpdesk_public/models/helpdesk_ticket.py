# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

from odoo import api, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def _retrieve_partner_from_email(self, vals):
        if "partner_email" in vals and not "partner_id" in vals:
            partner_id = (
                self.env["res.partner"]
                .sudo()
                .search([("email", "=", vals.get("partner_email"))])
            )
            vals["partner_id"] = partner_id.id

    @api.model
    def _retrieve_user_from_project(self, vals):
        if "project_id" in vals and not "user_id" in vals:
            project_id = (
                self.env["project.project"]
                .sudo()
                .search([("id", "=", vals.get("project_id"))])
            )
            vals["user_id"] = project_id.user_id.id

    @api.model
    def create(self, vals):
        self._retrieve_partner_from_email(vals)
        self._retrieve_user_from_project(vals)
        return super().create(vals)

    def _should_notify_new_ticket(self):
        res = super()._should_notify_new_ticket()
        if not res:
            res = self.env.context.get("public_ticket", False)
        return res
