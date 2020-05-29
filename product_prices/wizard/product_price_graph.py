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
# Written by Yann Papouin <y.papouin@dec-industrie.com>, May 2020

from odoo import api, fields, models, _


class product_price_graph(models.TransientModel):
    _name = 'product.price.graph'
    _description = 'Customize purchase report'

    product_id = fields.Many2one('product.product')
    default_purchase_price_graph_po_uom = fields.Char(
        string='Purchase Price Graph',
        related='product_id.default_purchase_price_graph_po_uom'
    )
    default_sell_price_graph = fields.Char(
        string='Sell Price Graph',
        related='product_id.default_sell_price_graph'
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if self.env.context.get('active_model') in (
            'product.template', 'product.product'
        ) and active_ids:
            res['product_id'] = active_ids[0]
        return res
