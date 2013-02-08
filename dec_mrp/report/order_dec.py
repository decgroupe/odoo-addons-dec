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

import time
from report import report_sxw
from tools.translate import _

class order_dec(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(order_dec, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_product_code':self._get_product_code,
            'get_product_name':self._get_product_name,
            'get_line':self._get_production_consume_move_status,
        })
        self.context = context
        
    def _get_product_code(self, move_line):
        if move_line and move_line.product_id and move_line.product_id.code:
            return '[%s]' % (move_line.product_id.code)
        else:
            return ''
         
    def _get_product_name(self, move_line):
#        stock_move_obj = self.pool.get('stock.move')
#        move_ids = stock_move_obj.search(cr, uid, [('id', '=', move_line.id)], context=context)     
#        for move in stock_move_obj.browse(cr, uid, move_ids, context=context):
        if move_line and move_line.product_id:
            return move_line.product_id.name
        else:
            return ''
        
    def _get_production_consume_move_status(self, mrp_production, move_line):
        
        result = {}
        cr = self.cr
        uid = self.uid
        context = self.context
        
        stock_move_obj = self.pool.get('stock.move')
        procurement_order_obj = self.pool.get('procurement.order')
        purchase_order_obj = self.pool.get('purchase.order')
        purchase_order_line_obj = self.pool.get('purchase.order.line')
        
        shipment = False
        procurement_order = False
        purchase_order = False
        purchase_order_line = False;
        
        
        shipment_move_ids = stock_move_obj.search(cr, uid, [('move_dest_id', '=', move_line.id)], context=context)     
        for shipment in stock_move_obj.browse(cr, uid, shipment_move_ids, context=context):
#            result['po'] = ''
#            result['name'] = shipment.name
#            result['state'] = shipment.state
#            result['picking'] = {}
#            result['picking']['name'] = shipment.picking_id and shipment.picking_id.name
#            result['picking']['state'] = shipment.picking_id and shipment.picking_id.state
            
            procurement_order_ids = procurement_order_obj.search(cr, uid, [('move_id', '=', shipment.id)], context=context)  
            for procurement_order in procurement_order_obj.browse(cr, uid, procurement_order_ids, context=context):
#                result['procurement_order'] = {}
#                result['procurement_order']['name'] = procurement_order.name
#                result['procurement_order']['state'] = procurement_order.state
#                result['procurement_order']['procure_method'] = procurement_order.procure_method
#                result['procurement_order']['date_planned'] = procurement_order.date_planned
                
                if procurement_order.purchase_id:
                    purchase_ids = purchase_order_obj.search(cr, uid, [('id', '=', procurement_order.purchase_id.id)], context=context)   
                    for purchase_order in purchase_order_obj.browse(cr, uid, purchase_ids, context=context): 
                        pass
#                        result['procurement_order']['purchase_order'] = {}
#                        result['procurement_order']['purchase_order']['name'] = purchase_order.name
#                        result['procurement_order']['purchase_order']['state'] = purchase_order.state
#                        result['po'] = '%s:%s' % (purchase_order.name, purchase_order.state)
                        
                purchase_line_ids = purchase_order_line_obj.search(cr, uid, [('origin_procurement_order_id', '=', procurement_order.id)], context=context)   
                for purchase_order_line in purchase_order_line_obj.browse(cr, uid, purchase_line_ids, context=context):       
#                    result['purchase_order_line'] = {}
#                    result['purchase_order_line']['name'] = purchase_order_line.name
#                    result['purchase_order_line']['state'] = purchase_order_line.state
#                    result['purchase_order_line']['date_planned'] = purchase_order_line.date_planned
                    
                    for purchase_order_line_moves in purchase_order_line.move_ids:   
#                        result['po'] = '%s (%s)' % (result['po'], purchase_order_line_moves.state)
#                        result['procurement_order']['purchase_order_line_move_state'] = purchase_order_line_moves.state
                        if purchase_order_line_moves.state != 'cancel':
                            break

        result['checked'] = False
        if shipment and procurement_order:
            if procurement_order.procure_method == 'make_to_stock':  
                if procurement_order.state == 'exception':
                    result['state'] = _('Not enough stock') 
                    result['pick'] = _('Dedicated') 
                elif procurement_order.state == 'ready' or procurement_order.state == 'done':
                    result['state'] = _('From stock')
                    result['pick'] = _('Dedicated') 
                    result['checked'] = True
                elif procurement_order.state == 'cancel':
                    result['state'] = _('From stock (automatic orderpoint canceled)')
                    result['pick'] =  _('Not dedicated') 
                    result['checked'] = True
                else:
                    result['state'] = _('From stock: ???')
                    result['pick'] =  _('Not dedicated') 
                    
            elif procurement_order.procure_method == 'make_to_order':  
                if procurement_order.state == 'exception':
                    result['state'] = _('Procurement exception (supplier error)')
                    result['pick'] = _('Dedicated') 
                elif procurement_order.state == 'running':
                    result['state'] = _('On procurement (purchase in progress)')
                    result['pick'] = _('Dedicated') 
                    
                    if purchase_order_line.order_id.state == 'draft':
                        result['state'] = _('On procurement (quotation)')
                    elif purchase_order_line.order_id.state == 'confirmed' or purchase_order_line.order_id.state == 'approved':
                        
                        if purchase_order_line_moves.state == 'assigned':
                            result['state'] = _('On procurement (purchase in progress)')
                        elif purchase_order_line_moves.state == 'done':
                            result['state'] = _('On procurement (delivered)')
                            result['checked'] = True
                        else:
                            result['state'] = _('On procurement (purchase ???)')
                    
                elif procurement_order.state == 'cancel':
                    result['pick'] =  _('Not dedicated') 
                    
                    if not purchase_order_line:
                        result['state'] = _('From stock (purchase deleted)')
                        result['checked'] = True
                    elif purchase_order_line.order_id.state == 'draft':
                        result['state'] = _('On quotation (procurement canceled)')
                    elif purchase_order_line.order_id.state == 'confirmed' or purchase_order_line.order_id.state == 'approved':
                        if purchase_order_line_moves.state == 'assigned':
                            result['state'] = _('On order (purchase in progress)')
                        elif purchase_order_line_moves.state == 'done':
                            result['state'] = _('On order (delivered)')
                            result['checked'] = True
                        else:
                            result['state'] = _('On order (purchase ???)')
                        
                    elif purchase_order_line.order_id.state == 'done':
                        result['state'] = _('On order (purchase done)')
                        result['checked'] = True
                    elif purchase_order_line.order_id.state == 'cancel':
                        result['state'] = _('From stock (procurement canceled)')
                        result['checked'] = True
                    else:
                        result['state'] = _('On order: ???')

                elif procurement_order.state == 'ready' or procurement_order.state == 'done':
                    result['state'] = _('On procurement (delivered)')
                    result['pick'] = _('Dedicated') 
                    result['checked'] = True
                else:
                    result['state'] = _('On procurement: ???')
                    result['pick'] =  _('Not dedicated') 

        
        return result

    def move_lines(self, mrp_production):
        result = []
        sub_total = {}
        order_lines = []
        res = {}
        
        result.append(res)
        return result
    
report_sxw.report_sxw('report.mrp.production.order.dec','mrp.production','addons-dec/dec_mrp/report/order_dec.rml',parser=order_dec,header='internal')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
