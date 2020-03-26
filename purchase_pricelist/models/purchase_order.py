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


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Mimic pricelist_id field from sale.order model
    # Lock type to purchase using domain attribute
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist',
        required=False,
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]
        },
        domain=[('type', '=', 'purchase')],
        help="Pricelist for current purchase order."
    )

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        super().onchange_partner_id()
        # Assign purchase pricelist from the partner property field
        if self.partner_id:
            values = {
                'pricelist_id':
                    self.partner_id.property_product_pricelist_purchase and
                    self.partner_id.property_product_pricelist_purchase.id
                    or False,
            }
            self.update(values)
