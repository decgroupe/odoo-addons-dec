# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Mar 2020

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Override sale pricelist field from addons/sale/models/sale.py
    # Lock type to sale using domain attribute
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist',
        required=True,
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)],
        },
        domain=[('type', '=', 'sale')],
        help="Pricelist for current sales order."
    )
