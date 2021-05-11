# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2021

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    partner_department_id = fields.Many2one(
        'res.country.department',
        related='partner_id.department_id',
        string="Partner's Department",
        store=True,
    )
    partner_state_id = fields.Many2one(
        'res.country.state',
        related='partner_id.state_id',
        string="Partner's State",
        store=True,
    )

