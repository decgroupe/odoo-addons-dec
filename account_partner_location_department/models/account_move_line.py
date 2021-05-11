# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    partner_department_id = fields.Many2one(
        'res.country.department',
        related='partner_id.department_id',
        string="Department",
        store=True,
    )
    partner_state_id = fields.Many2one(
        'res.country.state',
        related='partner_id.state_id',
        string="State",
        store=True,
    )
