# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2021

import re

from odoo import api, fields, models


class TypefastMixin(models.Model):
    _name = 'typefast.mixin'
    _description = "Typefast Mixin"

    typefast_name = fields.Char(
        compute="_compute_typefast",
        store=True,
    )
    
    @api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
    def _compute_typefast(self):
        for rec in self:
            # Strip everything but alphanumeric chars from the name
            rec.typefast_name = re.sub(r'\W+', '', rec[self._rec_name])

    def _prepare_typefast_search(self, name, args=None, operator='ilike'):
        if name and not args and operator == 'ilike':
            args = [
                ('|'),
                ('name', operator, name),
                ('typefast_name', operator, name),
            ]
            name = ''
        return name, args

    @api.model
    def _name_search(
        self, name, args=None, operator='ilike', limit=100, name_get_uid=None
    ):
        name, args = self._prepare_typefast_search(name, args, operator)
        return super()._name_search(
            name=name,
            args=args,
            operator=operator,
            limit=limit,
            name_get_uid=name_get_uid
        )
