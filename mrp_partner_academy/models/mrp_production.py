# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    partner_academy_id = fields.Many2one(
        'res.partner.academy',
        related='partner_id.academy_id',
        string="Partner's Academy",
        store=True,
    )
