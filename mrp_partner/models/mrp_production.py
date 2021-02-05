# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import models, api, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
    )

    zip_id = fields.Many2one(related='partner_id.zip_id')
