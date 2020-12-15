# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020


from odoo import fields, models, api


class ResCityZip(models.Model):
    _inherit = "res.city.zip"

    display_name = fields.Char(
        compute='_compute_new_display_name',
        store=True,
        index=True,
    )

    @api.multi
    @api.depends('name', 'city_id')
    def _compute_new_display_name(self):
        for rec in self:
            name = ["{} {}".format(rec.name, rec.city_id.name)]
            if rec.city_id.state_id:
                name.append(rec.city_id.state_id.name)
            if rec.city_id.country_id:
                name.append(rec.city_id.country_id.name)
            rec.display_name = ", ".join(name)
