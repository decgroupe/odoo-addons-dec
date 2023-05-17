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
        return "{} {}".format(self.name, self.city_id.name)

    @api.depends(
        "name", "city_id", "city_id.name", "city_id.state_id", "city_id.country_id"
    )
    def _compute_new_display_name(self):
        for rec in self:
            name = [rec.format_name()]
            country_id = rec.city_id.country_id
            if rec.city_id.state_id:
                if not country_id or (country_id and not country_id.hide_state):
                    name.append(rec.city_id.state_id.name)
            if country_id:
                name.append(country_id.name)
            rec.display_name = ", ".join(name)
