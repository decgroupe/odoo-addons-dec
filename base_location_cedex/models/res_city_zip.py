# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Dec 2020

from odoo import _, fields, models, api


class ResCityZip(models.Model):
    _inherit = "res.city.zip"

    cedex = fields.Char()

    _sql_constraints = [
        (
            'name_city_uniq', 'UNIQUE(name, cedex, city_id)',
            'You already have a zip with that code in the same city. '
            'The zip code must be unique within it\'s city'
        ),
    ]

    def format_name(self):
        self.ensure_one()
        res = "{} {}".format(self.name, self.city_id.name)
        if self.cedex:
            if self.cedex.lower() in ('cedex', '.', '-', '_'):
                res = _("{} Cedex").format(res)
            else:
                res = _("{} Cedex {}").format(res, self.cedex)
        return res

    @api.multi
    @api.depends(
        'name', 'cedex', 'city_id', 'city_id.name', 'city_id.state_id',
        'city_id.country_id'
    )
    def _compute_new_display_name(self):
        for rec in self:
            name = [rec.format_name()]
            if rec.city_id.state_id:
                name.append(rec.city_id.state_id.name)
            if rec.city_id.country_id:
                name.append(rec.city_id.country_id.name)
            rec.display_name = ", ".join(name)
