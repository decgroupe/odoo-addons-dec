# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class ResCityZip(models.Model):
    _inherit = "res.city.zip"

    display_name = fields.Char(
        compute="_compute_new_display_name",
        store=True,
        index=True,
    )

    def format_name(self):
        self.ensure_one()
        return f"{self.name} {self.city_id.name}"

    @api.depends(
        "name",
        "city_id",
        "city_id.name",
        "city_id.state_id",
        "city_id.country_id",
        "city_id.country_id.hide_state",
    )
    def _compute_new_display_name(self):
        for rec in self:
            name = [rec.format_name()]
            # country is a required field
            country_id = rec.city_id.country_id
            if rec.city_id.state_id and not country_id.hide_state:
                name.append(rec.city_id.state_id.name)
            name.append(country_id.name)
            rec.display_name = ", ".join(name)
