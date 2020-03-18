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


def rounding(f, r):
    import math
    if not r:
        return f
    return math.ceil(f / r) * r


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # taux_marge = marge_commerciale/cout_achat_HT * 100
    margin_percent = fields.Float(
        'Margin (%)', digits=(16, 2)
    )

     # taux_marque = marge_commerciale/prix_vente_HT * 100
    markup_percent = fields.Float(
        'Markup (%)', digits=(16, 2)
    )

    @api.onchange('markup_percent')
    def onchange_markup_percent(self): 
        vals = {}
        if self.purchase_price > 0 and self.discount < 100:
            if self.markup_percent < 100: 
                new_price_unit = self.purchase_price / float(1-self.discount/100.0) / float(1-self.markup_percent/100.0) 
                new_price_unit = rounding(new_price_unit, 0.01)
            else:
                new_price_unit = 0
                
            vals.update({'price_unit': new_price_unit})
        else:
            vals.update({'markup_percent': 0})
            
        self.update(vals)

    @api.onchange('purchase_price', 'product_uom_qty', 'price_unit', 'discount', 'margin')
    def _product_markup(self):
        vals = {}
        if (self.discount < 100) and (self.product_uom_qty > 0) and (self.price_unit > 0):
            new_markup_percent = self.margin/float(self.product_uom_qty) * 100 / float(self.price_unit - (self.price_unit * self.discount / 100.0))  
        else:
            new_markup_percent = 0

        vals.update({'markup_percent': new_markup_percent})
        self.update(vals)

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        # Store current markup
        previous_markup_percent = self.markup_percent
        # Recompute price_unit
        super().product_uom_change()
        # Restore previous markup and update price_unit
        self.markup_percent = previous_markup_percent
        self.onchange_markup_percent()
