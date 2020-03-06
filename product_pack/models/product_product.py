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


class product_product(models.Model):

    _inherit = 'product.product'

    # def get_product_available(self, cr, uid, ids, context=None):
    #     """ Calulate stock for packs, return  maximum stock that lets complete pack """
    #     result = {}
    #     for product in self.browse(cr, uid, ids, context=context):
    #         stock = super(product_product, self).get_product_available(
    #             cr, uid, [product.id], context=context
    #         )

    #         # Check if product stock depends on it's subproducts stock.
    #         if not product.stock_depends:
    #             result[product.id] = stock[product.id]
    #             continue

    #         first_subproduct = True
    #         pack_stock = 0

    #         pack_line_ids = None
    #         if product.sale_pack_line_ids:
    #             pack_line_ids = product.sale_pack_line_ids
    #         else:
    #             if product.purchase_pack_line_ids:
    #                 pack_line_ids = product.purchase_pack_line_ids

    #         # Check if the pack has subproducts
    #         if pack_line_ids:
    #             # Take the stock/virtual stock of all subproducts
    #             subproducts_stock = self.get_product_available(
    #                 cr,
    #                 uid, [line.product_id.id for line in pack_line_ids],
    #                 context=context
    #             )
    #             # Go over all subproducts, take quantity needed for the pack and its available stock
    #             for subproduct in pack_line_ids:
    #                 if first_subproduct:
    #                     subproduct_quantity = subproduct.quantity
    #                     subproduct_stock = subproducts_stock[
    #                         subproduct.product_id.id]
    #                     # Calculate real stock for current pack from the subproduct stock and needed quantity
    #                     pack_stock = math.floor(
    #                         subproduct_stock / subproduct_quantity
    #                     )
    #                     first_subproduct = False
    #                     continue
    #                 # Take the info of the next subproduct
    #                 subproduct_quantity_next = subproduct.quantity
    #                 subproduct_stock_next = subproducts_stock[
    #                     subproduct.product_id.id]
    #                 pack_stock_next = math.floor(
    #                     subproduct_stock_next / subproduct_quantity_next
    #                 )
    #                 # compare the stock of a subproduct and the next subproduct
    #                 if pack_stock_next < pack_stock:
    #                     pack_stock = pack_stock_next
    #             # result is the minimum stock of all subproducts
    #             result[product.id] = pack_stock
    #         else:
    #             result[product.id] = stock[product.id]
    #     return result
