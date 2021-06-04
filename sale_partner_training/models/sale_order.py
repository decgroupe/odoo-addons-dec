# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2021

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    training_specialty_ids = fields.Many2many(
        comodel_name='res.partner.training.specialty',
        string='Specialties',
        help='Educational Training Specialties related to this order.',
    )
