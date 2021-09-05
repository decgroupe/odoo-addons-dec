# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    partner_zip_id = fields.Many2one(
        'res.city.zip',
        related='partner_id.zip_id',
        string="Partner's ZIP",
        store=True,
    )
    partner_city_id = fields.Many2one(
        'res.city',
        related='partner_id.city_id',
        string="Partner's City",
        store=True,
    )
