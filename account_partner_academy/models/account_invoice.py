# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2021

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    partner_academy_id = fields.Many2one(
        'res.partner.academy',
        related='partner_id.academy_id',
        string="Partner's Academy",
        store=True,
    )
