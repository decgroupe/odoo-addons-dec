# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models


class RefVersion(models.Model):
    _name = 'ref.version'
    _description = 'Reference version'

    name = fields.Char(
        'Modification name',
        size=128,
        required=True,
    )
    version = fields.Integer(
        'Version',
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
