# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    # To replace with module `mrp_sale_info` ?

    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
    )
