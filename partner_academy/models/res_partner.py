# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_academy = fields.Many2one(
        'res.partner.academy',
        'Academy',
        help="Educational academy of the current partner.",
    )
