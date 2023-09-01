# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

import re

from odoo import api, fields, models
from odoo.osv import expression


class TypefastMixin(models.AbstractModel):
    _name = "typefast.mixin"
    _description = "Typefast Mixin"
    _typefast_options = {
        "source": "rec_name", # or name_get
        "strip": True,
    }

    typefast_name = fields.Char(
        compute="_compute_typefast",
        store=True,
    )

    @api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
    def _compute_typefast(self):
        for rec in self:
            rec.typefast_name = False
            if self._typefast_options.get("source") == "rec_name":
                field_type = self._fields[self._rec_name].type
                if field_type == "char":
                    rec.typefast_name = rec[self._rec_name]
                elif field_type == "many2one":
                    rec.typefast_name = rec[self._rec_name].display_name
            elif self._typefast_options.get("source") == "name_get":
                rec.typefast_name = rec.name_get()[0][1]

            if rec.typefast_name and self._typefast_options.get("strip"):
                # Strip everything but alphanumeric chars from the name
                rec.typefast_name = re.sub(r"\W+", "", rec.typefast_name)

    def _get_typefast_domain(self, name, operator):
        return [
            ("|"),
            ("name", operator, name),
            ("typefast_name", operator, name),
        ]

    def _prepare_typefast_search(self, name, args=None, operator="ilike"):
        if name and operator == "ilike":
            typefast_args = self._get_typefast_domain(name, operator)
            if args:
                args = expression.AND([args, typefast_args])
            else:
                args = typefast_args
            name = ""
        return name, args

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        name, args = self._prepare_typefast_search(name, args, operator)
        return super()._name_search(
            name=name,
            args=args,
            operator=operator,
            limit=limit,
            name_get_uid=name_get_uid,
        )
