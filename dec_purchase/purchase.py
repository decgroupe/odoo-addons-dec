# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

import time

from osv import fields
from osv import osv
from tools.translate import _

class purchase_order(osv.osv):
    _name = "purchase.order"
    _inherit = "purchase.order"
    


    def button_refresh_prices(self, cr, uid, ids, context={}):
        if not ids :
            return False
        for purchaseorder in self.browse(cr, uid, ids, context):
            if isinstance(purchaseorder.pricelist_id, osv.orm.browse_null) :
                raise osv.except_osv('Warning !', 'Please set the price list the purchase order')
            #we modify the requiered data in the line
            for line in purchaseorder.order_line :
                if  type(line.product_id) != osv.orm.browse_null and line.product_id:
                    res = line.product_id_change(
                                                    purchaseorder.pricelist_id.id,
                                                    line.product_id.id,
                                                    line.product_qty,
                                                    line.product_uom.id,
                                                    purchaseorder.partner_id.id, 
                                                    purchaseorder.date_order, 
                                                    purchaseorder.fiscal_position
                                                )
                else:
                    continue
                if not line.product_uom :
                    price_unit = 0.0
                else :
                    price_unit = res['value']['price_unit']
                
                self.pool.get('purchase.order.line').write(cr, uid, line.id, {'price_unit' : price_unit}, {})
        return True
    

purchase_order()


class purchase_order_line(osv.osv):

    _inherit = 'purchase.order.line'

    def _get_purchase_origin(self, cr, uid, ids, name, arg, context=None):
        res = {}      
        for purchase_order_line in self.browse(cr, uid, ids, context=context): 
            merge_origin = purchase_order_line.merge_origin or False
            procurement_origin = purchase_order_line.origin_procurement_order_id and purchase_order_line.origin_procurement_order_id.origin or False
  
            result = procurement_origin                 
            if merge_origin and merge_origin <> procurement_origin:
                if result:
                    if uid == 1:
                        result = '%s <<< %s' % (result, merge_origin) 
                else:
                    result = merge_origin
 
            res[purchase_order_line.id] = result
                
        return res
    
    PURCHASE_STATE_SELECTION = [
        ('draft', 'Request for Quotation'),
        ('wait', 'Waiting'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]
    
    PRODUCT_PROCURE_METHOD = [
        ('make_to_stock','Make to Stock'),
        ('make_to_order','Make to Order')
    ]
    
    PRODUCT_TYPE = [
        ('product','Stockable Product'),
        ('consu', 'Consumable'),
        ('service','Service')
    ]

    _columns = {
         'purchase_origin': fields.function(_get_purchase_origin, type="char", string='Procurement origin'),
         
         'product_procure_method': fields.related('product_id', 'procure_method', type='selection', selection=PRODUCT_PROCURE_METHOD, string="Product procurement Method"),
         'product_type': fields.related('product_id', 'type', type='selection', selection=PRODUCT_TYPE, string="Product type"),
         'order_origin': fields.related('order_id', 'origin', type='char', string="Purchase origin"),
         'order_state': fields.related('order_id', 'state', type='selection', selection=PURCHASE_STATE_SELECTION, string="Purchase state"),
    }

    _order = "id desc"

   

purchase_order_line()
