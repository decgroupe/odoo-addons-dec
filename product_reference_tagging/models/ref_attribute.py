# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models, _


class RefAttribute(models.Model):
    _inherit = 'ref.attribute'
    _name = _inherit

    tagging_ids = fields.Many2many(
        comodel_name='tagging.tags',
        relation='tagging_ref_attribute',
        column1='attribute_id',
        column2='tag_id',
        string='Tags',
    )
