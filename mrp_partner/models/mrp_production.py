# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import models, api, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    # TODO: partner_id is currently defined in mrp_sale module
    # it should be moved here and mrp_sale should depends on mrp_partner
    
    zip_id = fields.Many2one(related='partner_id.zip_id')
