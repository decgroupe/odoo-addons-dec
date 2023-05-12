# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    academy_id = fields.Many2one(
        comodel_name="res.partner.academy",
        string="Academy",
        help="Educational academy of the current partner.",
    )

    @api.onchange("email")
    def _onchange_email(self):
        self._set_academy_from_email(self.email)

    def _set_academy_from_email(self, email):
        if not email:
            return
        if "@" in email:
            domain = email.partition("@")[2]
            self._set_academy_from_domain(domain)

    def _set_academy_from_domain(self, domain):
        if not domain:
            return
        # Browse all records since an email_domain field can includes
        # multiple domain
        academy_ids = self.env["res.partner.academy"].search(
            [("email_domain", "!=", False)],
        )
        for academy_id in academy_ids:
            for academy_domain in academy_id.email_domain.split():
                if domain.endswith(academy_domain):
                    self.academy_id = academy_id
                    break
