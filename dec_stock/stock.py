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

class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = _name
        
    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        SUPER_USER = 1
        for pick in self.browse(cr, uid, ids, context=context):
            if uid <> SUPER_USER:
                raise osv.except_osv(_('Error'), _('You must be admin to execute delete action!'))
            
        return super(stock_picking, self).unlink(cr, uid, ids, context=context)

class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"
    

    def _get_move_origin(self, cr, uid, ids, name, arg, context=None):
        res = {}
        procurement_order_obj = self.pool.get('procurement.order')
        purchase_order_line_obj = self.pool.get('purchase.order.line')
        
        for move_line in self.browse(cr, uid, ids, context=context):  
            res[move_line.id] = False  
            
            parent_move_ids = self.search(cr, uid, [('move_dest_id', '=', move_line.id)], context=context) 
            for parent_move_line in self.browse(cr, uid, parent_move_ids, context=context):  
                if parent_move_line.production_id:
                    res[move_line.id] = parent_move_line.production_id.name
                    break
            else:
                purchase_order_line_ids = purchase_order_line_obj.search(cr, uid, [('move_ids', '=', move_line.id)], context=context) 
                for purchase_order_line in purchase_order_line_obj.browse(cr, uid, purchase_order_line_ids, context=context):
                    res[move_line.id] = purchase_order_line.purchase_origin
#                
#                
#                if purchase_order_line.origin_procurement_order_id:
#                    procurement_order_ids = procurement_order_obj.search(cr, uid, [('id', '=', purchase_order_line.origin_procurement_order_id.id)], context=context)  
#                    for procurement_order in procurement_order_obj.browse(cr, uid, procurement_order_ids, context=context):
#                        if procurement_order.origin:
#                            res[move_line.id] = procurement_order.origin
                
        return res


    def _get_move_final_location(self, cr, uid, ids, name, arg, context=None):
        res = {}       
        for move_line in self.browse(cr, uid, ids, context=context):             
            if move_line.move_dest_id and (move_line.product_id.id == move_line.move_dest_id.product_id.id) :
                recres = self._get_move_final_location(cr, uid, [move_line.move_dest_id.id], name=None, arg=None, context=context)
                if uid == 1: # Full path for admin only 
                    res[move_line.id] = move_line.location_dest_id.name + '>' + recres[move_line.move_dest_id.id] 
                else:
                    res[move_line.id] = recres[move_line.move_dest_id.id]        
            else:
                res[move_line.id] = move_line.location_dest_id.name
                
        return res

    _columns = {
         'move_origin': fields.function(_get_move_origin, type="char", string='Move origin', readonly=True),
         'move_final_location': fields.function(_get_move_final_location, type="char", string='Final location', readonly=True),
         'create_uid':  fields.many2one('res.users', 'Creator'),
         'write_uid':  fields.many2one('res.users', 'Last editor'),
    }

stock_move()


class product_product(osv.osv):
    _name = "product.product"
    _inherit= _name
    
    
    def search_unavailable(self, cr, uid, context=None):
        res = {}
        if context is None:
            context = {}
            
        product_obj = self.pool.get('product.product')
        products_ids = product_obj.search(cr, uid, [('purchase_ok', '=', True)], order='id', context=context)

        return products_ids

    
product_product()

