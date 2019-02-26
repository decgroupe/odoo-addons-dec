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
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class purchase_order(osv.osv):
    _name = "purchase.order"
    _inherit = "purchase.order"
    

    def _prepare_order_picking(self, cr, uid, order, context=None):
        result = super(purchase_order, self)._prepare_order_picking(cr, uid, order, context=context)
        
        # Overwrite picking date with approve date fom order
        result['date'] = order.date_approve
        return result
        
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
    
        # Hack to update all purchase lines at confirmation with their new delay
        product_supplierinfo = self.pool.get('product.supplierinfo')
        supplierinfo_ids = product_supplierinfo.search(cr, uid, [('name', '=', order.partner_id.name), ('product_id', '=', order_line.product_id.product_tmpl_id.id)])
        if supplierinfo_ids:
            supplierinfo = product_supplierinfo.browse(cr, uid, supplierinfo_ids[0], context=context)
            
            purchase_order_line = self.pool.get('purchase.order.line')
            dt = purchase_order_line._get_date_planned(cr, uid, supplierinfo, order.date_approve, context=context).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            
            # Update DB
            order_line.write({'date_planned': dt})
            # Also update current query
            order_line.date_planned = dt        
        
        result = super(purchase_order, self)._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=context)
        
        # Overwrite move date with approve date fom order
        result['date'] = order.date_approve
        return result
    
    '''
    _columns = {
        'origin': fields.char('Source Document', size=512, help="Reference of the document that generated this purchase order request."
        ),
     }
    '''
    def line_refresh_price(self, order, line, context=None):
        res = line.product_id_change(order.pricelist_id.id, line.product_id.id, line.product_qty, line.product_uom.id, 
                                        order.partner_id.id, order.date_order, order.fiscal_position, context=context)
        if not line.product_uom :
            price_unit = 0.0
        else :
            price_unit = res['value']['price_unit']
        return price_unit 

    def button_refresh_prices(self, cr, uid, ids, context=None):
        if not ids :
            return False
        for purchaseorder in self.browse(cr, uid, ids, context):
            if isinstance(purchaseorder.pricelist_id, osv.orm.browse_null) :
                raise osv.except_osv('Warning !', 'Please set the price list the purchase order')
            #we modify the required data in the line
            for line in purchaseorder.order_line :
                price_unit = self.line_refresh_price(purchaseorder, line, context=context)   
                if price_unit <> line.price_unit:             
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
                    pass
                    #if uid == 1:
                    #    result = '%s <<< %s' % (result, merge_origin) 
                else:
                    result = merge_origin
 
            res[purchase_order_line.id] = result
                
        return res
    
    def _get_sequence(self, cr, uid, context=None):
        if context is None:
            context = {}      
            
        return int(time.time())
    
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
        'sequence': fields.integer('Line Sequence', select=True),
        'purchase_origin': fields.function(_get_purchase_origin, type="char", string='Procurement origin'),
        'product_procure_method': fields.related('product_id', 'procure_method', type='selection', selection=PRODUCT_PROCURE_METHOD, string="Product procurement Method"),
        'product_type': fields.related('product_id', 'type', type='selection', selection=PRODUCT_TYPE, string="Product type"),
        'order_origin': fields.related('order_id', 'origin', type='char', string="Purchase origin"),
        'order_state': fields.related('order_id', 'state', type='selection', selection=PURCHASE_STATE_SELECTION, string="Purchase state"),
    }
    
    _defaults = {
        'sequence': _get_sequence,
    }
   
    _order = "order_id, sequence asc"

   

purchase_order_line()
