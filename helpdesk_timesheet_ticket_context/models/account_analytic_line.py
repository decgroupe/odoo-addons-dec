# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    ticket_id = fields.Many2one(
        domain="ticket_id_domain",
    )
    ticket_id_domain = fields.Binary(
        string="Ticket Domain",
        help="Dynamic domain used for the `ticket_id` field",
        compute="_compute_ticket_id_domain",
    )

    @api.onchange("ticket_id")
    def onchange_ticket_id(self):
        # if the currently assigned project is not the one of the ticket then unset it
        if self.ticket_id and self.project_id != self.ticket_id.project_id:
            self.project_id = False
        # do not call super() to avoid resetting the project_id to the one of the
        # ticket if the project_id is already set to a different one
        if not self.project_id:
            self.project_id = self.ticket_id.project_id
            self.task_id = self.ticket_id.task_id

    @api.depends("project_id")
    def _compute_ticket_id_domain(self):
        for rec in self:
            domain = []
            if rec.project_id:
                domain = [("project_id", "=", rec.project_id.id)]
            rec.ticket_id_domain = domain
