# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    warranty = fields.Integer(
        'Warranty period',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)],
        },
        help="Warranty delay in year(s)",
        default=2
    )
