# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    partner_academy_id = fields.Many2one(
        comodel_name='res.partner.academy',
        related='partner_id.academy_id',
        string="Partner's Academy",
        store=True,
    )
