# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

from odoo import api, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def _retrieve_partner_from_email(self, vals):
        """Retrieve the partner from the email if not set"""
        partner_email = vals.get("partner_email")
        if partner_email and "partner_id" not in vals:
            partner_id = (
                self.env["res.partner"].sudo().search([("email", "=", partner_email)])
            )
            vals["partner_id"] = partner_id.id

    @api.model
    def _retrieve_user_from_project(self, vals):
        """Retrieve the user from the project if not set"""
        project_raw_id = vals.get("project_id")
        if project_raw_id and "user_id" not in vals:
            project_id = (
                self.env["project.project"].sudo().search([("id", "=", project_raw_id)])
            )
            vals["user_id"] = project_id.user_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._retrieve_partner_from_email(vals)
            self._retrieve_user_from_project(vals)
        record_ids = super().create(vals_list)
        return record_ids

    def _should_notify_new_ticket(self):
        res = super()._should_notify_new_ticket()
        if not res:
            res = self.env.context.get("public_ticket", False)
        return res
