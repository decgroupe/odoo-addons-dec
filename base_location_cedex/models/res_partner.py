# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import _, api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange("zip_id")
    def _onchange_zip_id(self):
        super()._onchange_zip_id()
        if self.zip_id and self.zip_id.cedex:
            vals = {"city": self.zip_id.format_city_name_with_cedex()}
            self.update(vals)
