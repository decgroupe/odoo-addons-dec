# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    partner_academy_id = fields.Many2one(
        'res.partner.academy',
        related='partner_id.academy_id',
        string="Partner's Academy",
        store=True,
    )
