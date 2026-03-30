# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    phonecall_id = fields.Many2one(
        domain="phonecall_id_domain",
    )
    phonecall_id_domain = fields.Binary(
        string="Phone Call Domain",
        help="dynamic domain used for the `phonecall_id` field",
        compute="_compute_phonecall_id_domain",
    )

    @api.depends("project_id")
    def _compute_phonecall_id_domain(self):
        """Compute the dynamic domain for phonecall_id based on project_id."""
        for rec in self:
            domain = []
            if rec.project_id:
                domain = [("project_id", "=", rec.project_id.id)]
            rec.phonecall_id_domain = domain
