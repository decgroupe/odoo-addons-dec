# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    fax = fields.Char(
        related='partner_id.fax',
        store=True,
        readonly=False,
    )
