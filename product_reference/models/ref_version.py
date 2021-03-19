# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models, api


class RefVersion(models.Model):
    _name = 'ref.version'
    _description = 'Reference version'

    @api.model
    def _default_version(self):
        res = 1
        active_id = self._context.get('params', {}).get('id')
        active_model = self._context.get('params', {}).get('model')
        if not active_id or active_model != 'ref.reference':
            return res
        reference_id = self.env['ref.reference'].browse(active_id)
        for version_id in reference_id.version_ids:
            if version_id.version > res:
                res = version_id.version
        return res

    name = fields.Char(
        'Modification name',
        size=128,
        required=True,
    )
    version = fields.Integer(
        'Version',
        default=_default_version,
        required=True,
    )
    datetime = fields.Datetime(
        'Modification date',
        default=fields.Datetime.now,
    )
    author_id = fields.Many2one(
        'res.users',
        'Author',
        default=lambda self: self.env.user,
        oldname='author',
    )
    reference_id = fields.Many2one(
        'ref.reference',
        'Reference',
        oldname='reference',
    )
