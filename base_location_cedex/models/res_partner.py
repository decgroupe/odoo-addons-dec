# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import _, api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("zip_id")
    def _compute_city(self):
        if hasattr(super(), "_compute_city"):
            super()._compute_city()  # pragma: no cover
        for record in self:
            if record.zip_id and record.zip_id.cedex:
                record.city = self.zip_id.format_city_name_with_cedex()
