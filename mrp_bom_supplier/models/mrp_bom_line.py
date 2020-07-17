# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    landmark = fields.Char('Landmark')
    partner_id = fields.Many2one(
        'res.partner',
        'Supplier',
    )
