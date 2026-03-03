# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

import string

from odoo import api, fields, models
from odoo.exceptions import UserError

FMT_CHARSET = ["T", "A", "N"]
A_CHARSET = [c for c in string.ascii_uppercase]
N_CHARSET = [str(c) for c in range(0, 10)]
T_CHARSET = A_CHARSET + N_CHARSET


class RefProperty(models.Model):
    _name = "ref.property"
    _description = "Property"
    _rec_name = "name"
    _order = "name"

    name = fields.Char(
        string="Name",
        required=True,
    )
    format = fields.Char(
        string="Format",
        required=True,
    )
    fixed = fields.Boolean("Fixed values")
    attribute_ids = fields.One2many(
        comodel_name="ref.attribute",
        inverse_name="property_id",
        string="Attributes",
    )

    def write(self, vals):
        res = super().write(vals)
        return res

    @api.onchange("format")
    def onchange_format(self):
        self.ensure_one()
        if self.format:
            for c in self.format:
                if c.upper() not in FMT_CHARSET:
                    raise UserError(
                        self.env._(
                            "Invalid char %(c)s, only allowed chars are %(charset)s",
                            c=c,
                            charset=FMT_CHARSET,
                        )
                    )

    def _get_charset(self, index):
        if self.format[index] == "T":
            res = T_CHARSET
        elif self.format[index] == "A":
            res = A_CHARSET
        elif self.format[index] == "N":
            res = N_CHARSET
        else:
            res = []
        return res

    def validate_value(self, value):
        if not value:
            return False
        value = value.upper()
        valid_length = len(self.format)
        if len(value) != valid_length:
            raise UserError(
                self.env._(
                    "Invalid value length, the length must be %(length)d",
                    length=valid_length,
                )
            )

        for i, c in enumerate(value):
            charset = self._get_charset(i)
            if c not in charset:
                raise UserError(
                    self.env._(
                        "Invalid char %(c)s, an allowed char should be in %(charset)s",
                        c=c,
                        charset=charset,
                    )
                )
        return value

    def format_int(self, value):
        self.ensure_one()
        if "N" in self.format and "A" not in self.format and "T" not in self.format:
            return f"{str(value).zfill(len(self.format))}"
