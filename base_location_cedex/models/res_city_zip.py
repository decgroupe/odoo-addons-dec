# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

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
        custom_prefix = super().format_name()
        res = self.format_city_name_with_cedex(custom_prefix)
        return res

    def format_city_name_with_cedex(self, prefix=''):
        self.ensure_one()
        if not prefix:
            prefix = self.city_id.name
        res = prefix
        if self.cedex:
            if self.cedex.lower() in ('cedex', '.', '-', '_'):
                res = _("{} Cedex").format(res)
            else:
                res = _("{} Cedex {}").format(res, self.cedex)
        return res
