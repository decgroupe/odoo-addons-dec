# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ref_reference_line(models.Model):
    """ Description """

    _name = 'ref.reference.line'
    _description = 'Reference line'
    _rec_name = 'value'
    _order = 'sequence'

    reference = fields.Many2one('ref.reference', 'Reference', required=True)
    property = fields.Many2one('ref.property', 'Property', required=True)
    attribute_id = fields.Many2one('ref.attribute', 'Attribute')
    value = fields.Text('Value')
    sequence = fields.Integer('Position', required=True)

