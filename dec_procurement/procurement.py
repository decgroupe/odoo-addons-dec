# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import osv, fields
from tools.translate import _
import netsvc
import time
import decimal_precision as dp



class procurement_order(osv.osv):
    """
    Procurement Orders
    """
    _name = 'procurement.order'
    _inherit = _name
    

    _columns = {
        'product_supplier_id': fields.many2one('res.partner', 'Supplier'),
        'create_uid':  fields.many2one('res.users', 'Creator'),
        'write_uid':  fields.many2one('res.users', 'Last editor'),
    }
    
    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals, line_vals, context=None):
        """Create the purchase order from the procurement, using
           the provided field values, after adding the given purchase
           order line in the purchase order.

           Inherited in order to force supplier id from BoM in the purchase order lines

           :params procurement: the procurement object generating the purchase order
           :params dict po_vals: field values for the new purchase order (the
                                 ``order_line`` field will be overwritten with one
                                 single line, as passed in ``line_vals``).
           :params dict line_vals: field values of the single purchase order line that
                                   the purchase order will contain.
           :return: id of the newly created purchase order
           :rtype: int
        """
        partner_obj = self.pool.get('res.partner')
        pricelist_obj = self.pool.get('product.pricelist')
        uom_obj = self.pool.get('product.uom')
        
        if procurement.product_supplier_id and (procurement.product_supplier_id.id <> procurement.product_id.seller_id.id):
            address_id = partner_obj.address_get(cr, uid, [procurement.product_supplier_id.id], ['delivery'])['delivery']
            pricelist_id = procurement.product_supplier_id.property_product_pricelist_purchase.id
            uom_id = procurement.product_id.uom_po_id.id
            seller_qty = procurement.product_id.seller_qty
                    
            qty = uom_obj._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, uom_id)
            price = pricelist_obj.price_get(cr, uid, [pricelist_id], procurement.product_id.id, qty, procurement.product_supplier_id.id, {'uom': uom_id})[pricelist_id]  
            
            po_vals = dict(po_vals)
            po_vals['partner_id'] = procurement.product_supplier_id.id
            po_vals['partner_address_id'] = address_id
            po_vals['pricelist_id'] = pricelist_id    

            line_vals = dict(line_vals)
            line_vals['product_qty'] = qty
            line_vals['price_unit'] = price or 0.0

        return super(procurement_order, self).create_procurement_purchase_order(cr, uid, procurement, po_vals, line_vals, context=context)



procurement_order()


class stock_warehouse_orderpoint(osv.osv):
    _name = "stock.warehouse.orderpoint"
    _inherit = _name
    
    def _get_default_warehouse(self, cr, uid, context={}):
        result = False
        wareshouse_obj = self.pool.get('stock.warehouse')
        wareshouse_ids = wareshouse_obj.search(cr, uid, [], context=context)
         
        for warehouse in wareshouse_obj.browse(cr, uid, wareshouse_ids, context=context):
            result = warehouse.id
            break
        
        return result
    
    _columns = {
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', required=True, ondelete="cascade"),
    }
    
    _defaults = {
        'warehouse_id': _get_default_warehouse,
        'product_min_qty': lambda *a: 0.0,
        'product_max_qty': lambda *a: 1,
    }
