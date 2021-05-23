# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2021

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_shipping_academy_id = fields.Many2one(
        'res.partner.academy',
        related='partner_shipping_id.academy_id',
        string="Shipping Partner's Academy",
        store=True,
    )
