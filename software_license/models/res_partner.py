# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2025

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    license_ids = fields.One2many(
        comodel_name="software.license",
        compute="_compute_license",
        string="Licenses",
        copy=False,
        help="Licenses",
    )
    license_count = fields.Integer(
        compute="_compute_license",
        string="Number of Licenses",
    )

    @api.depends("license_ids", "is_company", "parent_id.is_company")
    def _compute_license(self):
        for rec in self:
            domain = rec._get_license_default_domain()
            rec.license_ids = self.env["software.license"].search(domain)
            rec.license_count = len(rec.license_ids)

    def action_view_licenses(self):
        return self.with_context(active_test=False).license_ids.action_view()

    def _get_license_default_domain(self):
        self.ensure_one()
        partner_id = self
        while partner_id and not partner_id.is_company:
            partner_id = partner_id.parent_id
        if not partner_id:
            partner_id = self
        # with an `on_change` event, we need to get database ID from origin
        if isinstance(partner_id.id, models.NewId) and partner_id._origin:
            pid = partner_id._origin.id
        else:
            pid = partner_id.id
        res = [
            ("partner_id", "child_of", pid),
            ("application_id.type", "=", "inhouse"),
        ]
        return res
