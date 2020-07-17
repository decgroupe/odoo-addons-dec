# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ref_property(models.Model):
    """ Description """

    _name = 'ref.property'
    _description = 'Property'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Text('Name', required=True)
    format = fields.Text('Format', required=True)
    fixed = fields.Boolean('Fixed values')
    attributes = fields.One2many('ref.attribute', 'owner')
