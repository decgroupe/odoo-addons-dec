# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ref_version(models.Model):
    _name = 'ref.version'
    _description = 'Reference version'

    name = fields.Char('Modification name', size=128, required=True)
    version = fields.Integer('Version', required=True)
    datetime = fields.Datetime('Modification date', default=fields.Datetime.now)
    author = fields.Many2one(
        'res.users', 'Author', default=lambda x, y, z, c: z
    )
    reference = fields.Many2one('ref.reference', 'Reference')
