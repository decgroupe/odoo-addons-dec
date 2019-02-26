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

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp

class mrp_attach_move_production(osv.osv_memory):
    _name = "mrp.attach.move.production"
    _description = "Link production to move out"

    _columns = {
        'production_id': fields.many2one('mrp.production', 'Production order', required=True, readonly=True, domain=[] ),
        'product_id': fields.related('production_id', 'product_id', type='many2one', relation='product.product', string='Product' ,required=True, readonly=True,),
        'move_id': fields.many2one('stock.move', 'Product move', required=True, help="", select=True),
    }

    def default_get(self, cr, uid, fields, context):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        production_id = context and context.get('active_id', False) or False
        res = super(mrp_attach_move_production, self).default_get(cr, uid, fields, context=context)
        
        if production_id:
            mrp_production_obj = self.pool.get('mrp.production')
            production = mrp_production_obj.browse(cr, uid, production_id, context=context) 
            if 'production_id' in fields:
                res.update({'production_id': production_id})
            if 'product_id' in fields:
                res.update({'product_id': production.product_id.id})
                
        return res
    

    def onchange_move_id(self, cr, uid, ids, picking_id, move_id, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if context is None:
            context = {}
            
        result = {}
        stock_move_obj = self.pool.get('stock.move')
        stock_picking_obj = self.pool.get('stock.picking')
        
        if move_id:
            move = stock_move_obj.browse(cr, uid, move_id, context=context)  
            if move.picking_id and move.picking_id.id != picking_id:
                result = {'picking_id': move.picking_id.id}

        return {'value': result}
    
    def do_attach(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if context is None:
            context = {}

        mrp_production_obj = self.pool.get('mrp.production')
        stock_move_obj = self.pool.get('stock.move')
        mrp_attach = self.browse(cr, uid, ids[0], context=context) 
        if mrp_attach.production_id:
            mrp_production = mrp_production_obj.browse(cr, uid, mrp_attach.production_id.id, context=context) 
            
            if mrp_attach.move_id:
                move_src_ids = stock_move_obj.search(cr, uid, [('move_dest_id', '=', mrp_attach.move_id.id)], context=context) 
                
                if move_src_ids:
                    raise osv.except_osv(_('Error !'),_('This move is already assigned.'))  
            
                if not mrp_production.move_prod_id and not move_src_ids:                   
                    data = {
                        'origin': ('%s:%s') % (mrp_production.origin or 'PROTO', mrp_attach.move_id.picking_id.origin),
                        'partner_id': mrp_attach.move_id.picking_id.partner_id.id,
                        'address_id': mrp_attach.move_id.picking_id.address_id.id,
                        'move_prod_id': mrp_attach.move_id.id,
                    }
                    
                    mrp_production_obj.write(cr, uid, [mrp_production.id], data, context=context)
                    
                    for move in mrp_production.move_created_ids: 
                        stock_move_obj.write(cr, uid, [move.id], {'move_dest_id': mrp_attach.move_id.id}, context=context)
            else:
                raise osv.except_osv(_('Error !'),_('You must select a move.'))
        else:
            raise osv.except_osv(_('Error !'),_('You must select a production order.'))
        
        return {}
    
mrp_attach_move_production()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
