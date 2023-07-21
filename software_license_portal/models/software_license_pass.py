# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import api, models


class SoftwareLicensePass(models.Model):
    _inherit = "software.license.pass"

    @api.model
    def _get_pass_default_portal_domain(self, request_partner_id):
        partner_id = request_partner_id
        while partner_id and not partner_id.is_company:
            partner_id = partner_id.parent_id
        if not partner_id:
            partner_id = request_partner_id
        return [
            ("partner_id", "child_of", partner_id.id),
            ("state", "=", "sent"),
        ]

    def deactivate(self, hardware_name):
        self.ensure_one()
        hardware_ids = self.license_ids.mapped("hardware_ids").filtered(
            lambda x: x.name == hardware_name
        )
        hardware_ids.unlink()
