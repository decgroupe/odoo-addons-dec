# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    partner_zip_id = fields.Many2one(
        'res.city.zip',
        related='partner_id.zip_id',
        string="Partner ZIP Location",
        store=True,
    )
    partner_city_id = fields.Many2one(
        'res.city',
        related='partner_id.city_id',
        string="Partner City",
        store=True,
    )
