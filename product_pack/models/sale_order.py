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


class sale_order(models.Model):
    
    _inherit = 'sale.order'

    def create(self, cr, uid, vals, context=None):
        result = super(sale_order, self).create(cr, uid, vals, context)
        self.expand_packs(cr, uid, [result], context)
        return result

    def write(self, cr, uid, ids, vals, context=None):
        result = super(sale_order, self).write(cr, uid, ids, vals, context)
        self.expand_packs(cr, uid, ids, context)
        return result

    def copy(self, cr, uid, ids, vals, context=None):
        result = super(sale_order, self).copy(cr, uid, ids, vals, context)
        return result

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}

        result = super(sale_order,
                       self).copy_data(cr, uid, id, default, context=context)

        def copy_data_filter(line):
            # line is tuple with data a position 3 tuple(0,0,{})
            return line[2].get('pack_delete', False)

        if result.has_key('abstract_line_ids'):
            # We create a list comprehension by filtering data and removing lines to delete
            result['abstract_line_ids'] = [
                x
                for x in result['abstract_line_ids'] if not copy_data_filter(x)
            ]

        return result

    def expand_packs(self, cr, uid, ids, context={}, depth=1):
        if depth == 10:
            return
        updated_orders = []
        for order in self.browse(cr, uid, ids, context):

            fiscal_position = order.fiscal_position and self.pool.get(
                'account.fiscal.position'
            ).browse(cr, uid, order.fiscal_position, context) or False

            # The reorder variable is used to ensure lines of the same pack go right after their
            # parent.
            # What the algorithm does is check if the previous item had children. As children items
            # must go right after the parent if the line we're evaluating doesn't have a parent it
            # means it's a new item (and probably has the default 10 sequence number - unless the
            # appropiate c2c_sale_sequence module is installed). In this case we mark the item for
            # reordering and evaluate the next one. Note that as the item is not evaluated and it might
            # have to be expanded it's put on the queue for another iteration (it's simple and works well).
            # Once the next item has been evaluated the sequence of the item marked for reordering is updated
            # with the next value.
            sequence = -1
            reorder = []
            last_had_children = False
            for line in order.order_line:
                if last_had_children and not line.pack_parent_line_id:
                    reorder.append(line.id)
                    if line.product_id.sale_pack_line_ids and not order.id in updated_orders:
                        updated_orders.append(order.id)
                    continue

                sequence += 1

                if sequence > line.sequence:
                    self.pool.get('sale.order.line').write(
                        cr, uid, [line.id], {
                            'sequence': sequence,
                        }, context
                    )
                else:
                    sequence = line.sequence

                if line.state != 'draft':
                    continue
                if not line.product_id:
                    continue

                # If pack was already expanded (in another create/write operation or in
                # a previous iteration) don't do it again.
                if not line.pack_expand or line.pack_child_line_ids:
                    last_had_children = True
                    continue
                last_had_children = False

                for subline in line.product_id.sale_pack_line_ids:
                    sequence += 1

                    subproduct = subline.product_id
                    quantity = subline.quantity * line.product_uom_qty

                    if line.product_id.fixed_sale_price:
                        price = 0.0
                        discount = 0.0
                    else:
                        pricelist = order.pricelist_id.id
                        price = self.pool.get('product.pricelist').price_get(
                            cr, uid, [pricelist], subproduct.id, quantity,
                            order.partner_id.id, {
                                'uom': subproduct.uom_id.id,
                                'date': order.date_order,
                            }
                        )[pricelist]
                        discount = line.discount

                    # Obtain product name in partner's language
                    ctx = {'lang': order.partner_id.lang}
                    subproduct_name = self.pool.get('product.product').browse(
                        cr, uid, subproduct.id, ctx
                    ).name

                    tax_ids = self.pool.get('account.fiscal.position').map_tax(
                        cr, uid, fiscal_position, subproduct.taxes_id
                    )

                    if subproduct.uos_id:
                        uos_id = subproduct.uos_id.id
                        uos_qty = quantity * subproduct.uos_coeff
                    else:
                        uos_id = False
                        uos_qty = quantity

                    vals = {
                        'order_id':
                            order.id,
                        'name':
                            '%s %s' %
                            ('>' * (line.pack_depth + 1), subproduct_name),
                        'sequence':
                            sequence,
                        'delay':
                            subproduct.sale_delay or 0.0,
                        'product_id':
                            subproduct.id,
                        'procurement_id':
                            line.procurement_id and line.procurement_id.id
                            or False,
                        'price_unit':
                            price,
                        'tax_id': [(6, 0, tax_ids)],
                        'type':
                            subproduct.procure_method,
                        'property_ids': [(6, 0, [])],
                        'address_allotment_id':
                            False,
                        'product_uom_qty':
                            quantity,
                        'product_uom':
                            subproduct.uom_id.id,
                        'product_uos_qty':
                            uos_qty,
                        'product_uos':
                            uos_id,
                        'product_packaging':
                            False,
                        'move_ids': [(6, 0, [])],
                        'discount':
                            discount,
                        'number_packages':
                            False,
                        'notes':
                            subproduct.description_sale,
                        'th_weight':
                            False,
                        'state':
                            'draft',
                        'pack_parent_line_id':
                            line.id,
                        'pack_depth':
                            line.pack_depth + 1,
                    }

                    # It's a control for the case that the nan_external_prices was installed with the product pack
                    if 'prices_used' in line:
                        vals['prices_used'] = line.prices_used

                    self.pool.get('sale.order.line').create(
                        cr, uid, vals, context
                    )
                    if not order.id in updated_orders:
                        updated_orders.append(order.id)

                for id in reorder:
                    sequence += 1
                    self.pool.get('sale.order.line').write(
                        cr, uid, [id], {
                            'sequence': sequence,
                        }, context
                    )

        if updated_orders:
            # Try to expand again all those orders that had a pack in this iteration.
            # This way we support packs inside other packs.
            self.expand_packs(cr, uid, ids, context, depth + 1)
        return

