# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from string import ascii_uppercase, ascii_lowercase

from odoo import fields, models, api
from odoo.tools import remove_accents

import unicodedata


class ResCity(models.Model):
    _inherit = "res.city"

    caps_count = fields.Integer(
        compute='_compute_caps',
        store=True,
    )
    caps_ratio = fields.Float(
        compute='_compute_caps',
        store=True,
    )
    normalized_name = fields.Char(
        compute='_compute_caps',
        store=True,
    )

    @api.depends('name')
    def _compute_caps(self):
        for rec in self:
            alpha_count = sum(
                1 for c in rec.name if c.upper() in ascii_uppercase
            )
            rec.caps_count = sum(1 for c in rec.name if c.isupper())
            rec.caps_ratio = rec.caps_count / alpha_count

            # Create a normalized name to easilly find duplicates
            s_name = remove_accents(rec.name.lower())
            rec.normalized_name = ''.join(
                c for c in s_name if c in ascii_lowercase
            )

    @api.model
    def read_group(
        self,
        domain,
        fields,
        groupby,
        offset=0,
        limit=None,
        orderby=False,
        lazy=True
    ):
        res = super().read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy
        )
        if 'normalized_name' in groupby:
            filtered_res = []
            for value in res:
                if value['normalized_name_count'] > 1:
                    filtered_res.append(value)
            res = filtered_res
        return res