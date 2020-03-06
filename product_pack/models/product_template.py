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

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class product_template(models.Model):

    _name = "product.template"
    _inherit = _name

    stock_depends = fields.Boolean(
        'Stock depends of components',
        help='Mark if pack stock is calculated from component stock'
    )
    sale_pack_line_ids = fields.One2many(
        'product.pack.saleline',
        'parent_product_id',
        'Pack Products',
        help='List of products that are part of this pack.'
    )
    fixed_sale_price = fields.Boolean(
        'Pack has fixed price',
        default=True,
        help='''Mark this field if the price of the pack should be fixed. 
        Do not mark it if the price should be calculated from the sum 
        of the prices of the products in the pack.'''
    )
    purchase_pack_line_ids = fields.One2many(
        'product.pack.purchaseline',
        'parent_product_id',
        'Pack Products',
        help='List of products that are part of this pack.'
    )
    fixed_purchase_price = fields.Boolean(
        'Pack has fixed price',
        default=True,
        help='''Mark this field if the price of the pack should be fixed. 
        Do not mark it if the price should be calculated from the sum 
        of the prices of the products in the pack.'''
    )

    def write(self, cr, uid, ids, vals, context=None):
        if 'uom_po_id' in vals:
            pack_saleline_obj = self.pool.get('product.pack.saleline')
            pack_purchaseline_obj = self.pool.get('product.pack.purchaseline')
            new_uom = self.pool.get('product.uom').browse(
                cr, uid, vals['uom_po_id'], context=context
            )
            if new_uom:
                for product in self.browse(cr, uid, ids, context=context):
                    old_uom = product.uom_po_id
                    pack_saleline_ids = pack_saleline_obj.search(
                        cr,
                        uid, [('product_id', '=', product.id)],
                        context=context
                    )
                    pack_purchaseline_ids = pack_purchaseline_obj.search(
                        cr,
                        uid, [('product_id', '=', product.id)],
                        context=context
                    )
                    if (old_uom.category_id.id != new_uom.category_id.id
                       ) and (pack_saleline_ids or pack_purchaseline_ids):
                        raise osv.except_osv(
                            _('UoM categories Mismatch!'),
                            _('This product is used in a pack (%s,%s)') % (
                                str(pack_saleline_ids),
                                str(pack_purchaseline_ids)
                            ) + '\n\n' + _(
                                "New UoM '%s' must belong to same UoM category '%s' as of old UoM '%s'. If you need to change the unit of measure, you may desactivate this product from the 'Procurement & Locations' tab and create a new one."
                            ) % (
                                new_uom.name,
                                old_uom.category_id.name,
                                old_uom.name,
                            )
                        )
        return super(product_template,
                     self).write(cr, uid, ids, vals, context=context)
