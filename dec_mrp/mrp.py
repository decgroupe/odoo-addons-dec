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

from datetime import datetime
from osv import osv, fields
import decimal_precision as dp
from tools import float_compare
from tools.translate import _
import netsvc
import time
import tools
import logging

def rounding(f, r):
    import math
    if not r:
        return f
    return math.ceil(f / r) * r


class mrp_bom(osv.osv):
    _name = "mrp.bom"
    _inherit="mrp.bom"
    
    
    def _bom_explode(self, cr, uid, bom, factor, properties=[], addthis=False, level=0, routing_id=False):
        """ Finds Products and Work Centers for related BoM for manufacturing order.
        @param bom: BoM of particular product.
        @param factor: Factor of product UoM.
        @param properties: A List of properties Ids.
        @param addthis: If BoM found then True else False.
        @param level: Depth level to find BoM lines starts from 10.
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """
        routing_obj = self.pool.get('mrp.routing')
        factor = factor / (bom.product_efficiency or 1.0)
        factor = rounding(factor, bom.product_rounding)
        if factor < bom.product_rounding:
            factor = bom.product_rounding
        result = []
        result2 = []
        phantom = False
        if bom.type == 'phantom' and not bom.bom_lines:
            newbom = self._bom_find(cr, uid, bom.product_id.id, bom.product_uom.id, properties)
            
            if newbom:
                res = self._bom_explode(cr, uid, self.browse(cr, uid, [newbom])[0], factor*bom.product_qty, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
                phantom = True
            else:
                phantom = False
        if not phantom:
            if addthis and not bom.bom_lines:
                result.append(
                {
                    'name': bom.product_id.name,
                    'product_id': bom.product_id.id,
                    'product_qty': bom.product_qty * factor,
                    'product_uom': bom.product_uom.id,
                    'product_uos_qty': bom.product_uos and bom.product_uos_qty * factor or False,
                    'product_uos': bom.product_uos and bom.product_uos.id or False,
                    
                    #YP
                    'supplier_id': bom.partner_id and bom.partner_id.id,
                })
            routing = (routing_id and routing_obj.browse(cr, uid, routing_id)) or bom.routing_id or False
            if routing:
                for wc_use in routing.workcenter_lines:
                    wc = wc_use.workcenter_id
                    d, m = divmod(factor, wc_use.workcenter_id.capacity_per_cycle)
                    mult = (d + (m and 1.0 or 0.0))
                    cycle = mult * wc_use.cycle_nbr
                    result2.append({
                        'name': tools.ustr(wc_use.name) + ' - '  + tools.ustr(bom.product_id.name),
                        'workcenter_id': wc.id,
                        'sequence': level+(wc_use.sequence or 0),
                        'cycle': cycle,
                        'hour': float(wc_use.hour_nbr*mult + ((wc.time_start or 0.0)+(wc.time_stop or 0.0)+cycle*(wc.time_cycle or 0.0)) * (wc.time_efficiency or 1.0)),
                    })
            for bom2 in bom.bom_lines:
                res = self._bom_explode(cr, uid, bom2, factor, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
        return result, result2
    
    
    def get_purchase_price(self, cr, uid, ids, context=None):
        result = 0.0
        if context is None:
            context = {}            

        pricelist_pool = self.pool.get('product.pricelist')
        for bom_line in self.browse(cr, uid, ids, context=context):
            partner_id = bom_line.partner_id
            if not partner_id:
                partner_id = bom_line.product_id.seller_id
                     
            if partner_id and partner_id.id <> bom_line.product_id.company_id.partner_id.id:
                pricelist = partner_id.property_product_pricelist_purchase
                if pricelist:
                    price = pricelist_pool.price_get(cr,uid,[pricelist.id], bom_line.product_id.id, bom_line.product_qty, partner_id.id, {
                            'uom': bom_line.product_uom.id,
                            'date': time.strftime('%Y-%m-%d'),
                            })[pricelist.id]
            else:
                price = bom_line.product_id.standard_price
                
            result = result + (price * bom_line.product_qty)
            
        return result
    
    def get_cost_price(self, cr, uid, ids, context=None):
        result = {}
        if context is None:
            context = {}     
            
        for id in ids:
            bom_line_ids = self.search(cr, uid, [('bom_id', '=', id)], context=context) 
            purchase_price = self.get_purchase_price(cr, uid, bom_line_ids, context=context)
            result[id] = purchase_price
                
        return result       
    
    _columns = {
	    'code': fields.char('Reference', size=64),
        'landmark': fields.char('Landmark', size=64),
        'partner_id': fields.many2one('res.partner', 'Supplier'),
        #'purchase_price': fields.function(_get_purchase_price, string='Purchase price', digits_compute=dp.get_precision('Purchase Price'), help="Purchase price based on partner pricelist"), 
        #'cost_price': fields.function(_get_cost_price, string='Cost price', digits_compute=dp.get_precision('Purchase Price'), help="Total cost price of current BoM"), 
    }

mrp_bom()

class stock_move(osv.osv):
    _name = "stock.move"
    _inherit="stock.move"
    
    
    def _get_status(self, cr, uid, ids, field_names, arg, context=None):
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
        
        stock_move_obj = self.pool.get('stock.move')
        procurement_order_obj = self.pool.get('procurement.order')
        
        for id in ids:
            res[id] = {}.fromkeys(field_names, False)
            
        shipment_move_ids = stock_move_obj.search(cr, uid, [('move_dest_id', 'in', ids)], context=context)   
        shipment_move_ids = shipment_move_ids + ids             
        procurement_order_ids = procurement_order_obj.search(cr, uid, [('move_id', 'in', shipment_move_ids)], context=context)  
        for procurement_order in procurement_order_obj.browse(cr, uid, procurement_order_ids, context=context):
            
            if procurement_order.move_id.product_id == procurement_order.move_id.move_dest_id.product_id:  
                i = procurement_order.move_id.move_dest_id.id 
            else:
                i = procurement_order.move_id.id 
                
            purchase_move_ids = stock_move_obj.search(cr, uid, [('move_dest_id', '=', procurement_order.move_id.id)], context=context)    
            purchase_move = len(purchase_move_ids)>0 and stock_move_obj.browse(cr, uid, purchase_move_ids, context=context)[0]
                            
            if procurement_order.procure_method == 'make_to_stock':  
                if procurement_order.state == 'exception':
                    res[i]['status_status'] = _('Not enough stock') 
                    res[i]['status_dedicated'] = _('Dedicated') 
                elif (procurement_order.state == 'ready' or procurement_order.state == 'done') and procurement_order.product_id.type == 'product':
                    res[i]['status_status'] = _('From stock')
                    res[i]['status_dedicated'] = _('Dedicated') 
                    res[i]['status_received'] = True
                elif (procurement_order.state == 'ready' or procurement_order.state == 'done') and procurement_order.product_id.type == 'consu':
                    res[i]['status_status'] = _('Consumable')
                    res[i]['status_dedicated'] = _('From workshop or manual picking') 
                    res[i]['status_received'] = True
                elif procurement_order.state == 'cancel':
                    res[i]['status_status'] = _('From stock (automatic orderpoint canceled)')
                    res[i]['status_dedicated'] =  _('Not dedicated') 
                    res[i]['status_received'] = True
                else:
                    res[i]['status_status'] = _('From stock: ???')
                    res[i]['status_dedicated'] =  _('Not dedicated') 
   
            elif procurement_order.procure_method == 'make_to_order':  
                if procurement_order.state == 'exception':
                    res[i]['status_status'] = _('Procurement exception (supplier error)')
                    res[i]['status_dedicated'] = _('Dedicated') 
                elif procurement_order.state == 'running':
                    res[i]['status_status'] = _('On procurement (purchase in progress)')
                    res[i]['status_dedicated'] = _('Dedicated') 
                    
                    if procurement_order.purchase_id:
                        res[i]['status_dedicated'] =  ('%s (%s: %s)') % (res[i]['status_dedicated'], procurement_order.purchase_id.name, procurement_order.purchase_id.partner_id.name)
                        
                        if procurement_order.purchase_id.state == 'draft':
                            res[i]['status_status'] = _('On procurement (quotation)')
                        elif procurement_order.purchase_id.state == 'confirmed' or procurement_order.purchase_id.state == 'approved' or procurement_order.purchase_id.state == 'except_picking':
                            
                            if purchase_move and purchase_move.state == 'assigned':
                                if len(purchase_move_ids) == 1:
                                    res[i]['status_status'] = _('On procurement (purchase in progress)')
                                else:
                                    res[i]['status_status'] = _('On procurement (partially delivered)')
                            elif purchase_move and purchase_move.state == 'done':
                                res[i]['status_status'] = _('On procurement (delivered)')
                                res[i]['status_received'] = True
                            else:
                                res[i]['status_status'] = _('On procurement (purchase ???)')
                                
                            if procurement_order.purchase_id.state == 'except_picking':
                                res[i]['status_status'] = res[i]['status_status'] + _('(Purchase exception)')
                        else:
                            res[i]['status_status'] = _('On procurement ???')
                    
                elif procurement_order.state == 'cancel':
                    res[i]['status_status'] = _('From stock (procurement canceled)')
                    res[i]['status_dedicated'] =  _('Not dedicated') 
                    res[i]['status_received'] = True
                    
                    if not procurement_order.purchase_id or not purchase_move:
                        res[i]['status_status'] = _('From stock (purchase deleted)')
                        res[i]['status_received'] = True
                    elif procurement_order.purchase_id.state == 'draft':
                        res[i]['status_status'] = _('On quotation (procurement canceled)')
                    elif procurement_order.purchase_id.state == 'confirmed' or procurement_order.purchase_id.state == 'approved':
                        if purchase_move and purchase_move.state == 'assigned':
                            res[i]['status_status'] = _('On order (%s, %s)') % (procurement_order.purchase_id.name, procurement_order.purchase_id.partner_id.name)
                        elif purchase_move and purchase_move.state == 'done':
                            res[i]['status_status'] = _('On order (delivered)')
                            res[i]['status_received'] = True
                        else:
                            res[i]['status_status'] = _('On order (purchase ???)')
                        
                    elif procurement_order.purchase_id.state == 'done':
                        res[i]['status_status'] = _('On order (purchase done)')
                        res[i]['status_received'] = True
                    elif procurement_order.purchase_id.state == 'cancel':
                        res[i]['status_status'] = _('From stock (procurement canceled)')
                        res[i]['status_received'] = True
                    else:
                        res[i]['status_status'] = _('On order: ???')

                elif procurement_order.state == 'ready' or procurement_order.state == 'done':
                    res[i]['status_status'] = _('On procurement (delivered)')
                    res[i]['status_dedicated'] = _('Dedicated') 
                    res[i]['status_dedicated'] =  ('%s (%s: %s)') % (res[i]['status_dedicated'], procurement_order.purchase_id and procurement_order.purchase_id.name, procurement_order.purchase_id and procurement_order.purchase_id.partner_id and procurement_order.purchase_id.partner_id.name)
                    res[i]['status_received'] = True
                else:
                    res[i]['status_status'] = _('On procurement ???')
                    res[i]['status_dedicated'] =  _('Not dedicated') 

        return res
    
    _columns = {
        'status_status': fields.function(_get_status, type='char', string='Status', multi='group_get_status'),
        'status_dedicated': fields.function(_get_status, type='char',  string='Dedicated', multi='group_get_status'),
        'status_received': fields.function(_get_status, type='boolean', string='Received', multi='group_get_status'),
    }
    
stock_move()



class mrp_production(osv.osv):
    _name = 'mrp.production'
    _inherit="mrp.production"
    
    
    def _get_late(self, cr, uid, ids, fieldnames, args, context=None):
        """ Get production late status.
        @param prop: Name of field.
        @param unknow_none:
        @return: Dictionary of values.
        """
        result = {}
        for prod in self.browse(cr, uid, ids, context=context):
            if prod.date_planned < prod.date_finished:
                result[prod.id] = True
            else:
                result[prod.id] = False 
                             
        return result
    
    def _make_production_line_procurement(self, cr, uid, production_line, shipment_move_id, context=None):
        wf_service = netsvc.LocalService("workflow")
        procurement_order = self.pool.get('procurement.order')
        production = production_line.production_id
        
        # YP: Override source for consumable products
        if production_line.product_id.type == 'consu':  
            location_id = production_line.product_id.product_tmpl_id.property_stock_production.id
        else:
            location_id = production.location_src_id.id
            
        date_planned = production.date_planned
        origin = (production.origin or '').split(':')[0]
        if origin:
            origin += ':' 
        procurement_origin = origin + production.name   
        if production_line.product_id.type == 'service': 
            procurement_name = '[%s] %s' % (production.bom_id.name, production.product_id.name)
        else:
            procurement_name = '%s (%s,%s,%s)' % (procurement_origin,production_line.product_id.type, production_line.product_id.procure_method, production_line.product_id.supply_method) 
         
        procurement_fields = {
                    'name': procurement_name,
                    'origin': procurement_origin,
                    'date_planned': date_planned,
                    'product_id': production_line.product_id.id,
                    'product_qty': production_line.product_qty,
                    'product_uom': production_line.product_uom.id,
                    'product_uos_qty': production_line.product_uos and production_line.product_qty or False,
                    'product_uos': production_line.product_uos and production_line.product_uos.id or False,
                    'location_id': location_id,
                    'procure_method': production_line.product_id.procure_method,
                    'move_id': shipment_move_id,
                    'company_id': production.company_id.id,
                    
                    # YP
                    'product_supplier_id': production_line.supplier_id and production_line.supplier_id.id or False,
                }
        
        procurement_id = procurement_order.create(cr, uid, procurement_fields)
        wf_service.trg_validate(uid, procurement_order._name, procurement_id, 'button_confirm', cr)
        return procurement_id
    
    def _get_sale_dates(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
        
        sale_order_obj = self.pool.get('sale.order')
        
        for id in ids:
            res[id] = {}.fromkeys(field_names, False)
            
        for prod in self.browse(cr, uid, ids, context=context):
            sale_order_ids = sale_order_obj.search(cr, uid, [('name', '=', prod.sale_name)], context=context)   
            
            for sale_order in sale_order_obj.browse(cr, uid, sale_order_ids, context=context):
                for f in field_names:
                    if f == 'sale_requested_date':
                        res[prod.id][f] = sale_order.requested_date  
                    if f == 'sale_commitment_date':
                        res[prod.id][f] = sale_order.commitment_date  
            
        return res
    

    def _picked_rate(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
        
        move_obj = self.pool.get('stock.move') 

        for prod in self.browse(cr, uid, ids, context=context):
            ready_count = 0
            total_count = 0
            
            count_move = []
            alt_moves = []
            for move in prod.move_all_src_ids:
                move.product_id.name
                total_count += 1
                if move.state in ('assigned', 'done'):
                    ready_count += 1
                elif move.state in ('waiting'):
                    alt_moves += [move.id]
                    
            move_ids = move_obj.search(cr, uid, [('move_dest_id', 'in', alt_moves)], context=context) 
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                if move.state in ('assigned'):
                    ready_count += 1
                   
            if total_count > 0: 
                res[prod.id] = float(ready_count)/float(total_count) * 100
            else:   
                res[prod.id] = 0.0  
        
        return res
    

    def _get_tested(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
        
        for id in ids:
            res[id] = {}.fromkeys(field_names, False)
            
        for prod in self.browse(cr, uid, ids, context=context):
            total_count = 0
            ready_count = 0
            for task in prod.task_ids:
                total_count += 1
                if task.state in ('done','cancel'):
                    ready_count += 1
               
            res[prod.id]['tested_count'] = total_count    
            if total_count > 0: 
                res[prod.id]['tested_rate'] = float(ready_count)/float(total_count) * 100
            else:   
                res[prod.id]['tested_rate'] = 0.0          
        
        return res
    
    def _get_view_name(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
             
        for prod in self.browse(cr, uid, ids, context=context):
            res[prod.id] = '%s: %s (%s)' % (prod.name, prod.product_id.name, prod.bom_id.name)  
            
        return res  
    
    
    def _get_invalid_move_prod(self, cr, uid, ids, fieldnames, args, context=None):
        result = {}
        for prod in self.browse(cr, uid, ids, context=context):
            if not prod.move_prod_id or (prod.move_prod_id and prod.move_prod_id.state == 'cancel'):
                result[prod.id] = True
            else:
                result[prod.id] = False 
                             
        return result

    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True, readonly=False, states={'draft':[('readonly',False)]}),
        'bom_id': fields.many2one('mrp.bom', 'Bill of Material', domain=[('bom_id','=',False)], required=True, readonly=False, states={'draft':[('readonly',False),('required',False)]}),
        'duration': fields.float('Duration'),
        'date_start': fields.date('Start Date', select=True),
        'date_finished': fields.date('End Date', select=True),
        'assigned_workcenter': fields.many2one('mrp.workcenter', 'Assigned to', required=False),
        'late': fields.function(_get_late, type='boolean', string='Late', store=True),
        'view_name': fields.function(_get_view_name, string='View name', type='char'), 
        'picked_rate': fields.function(_picked_rate, string='Picked', type='float', store=True),
        'move_all_src_ids': fields.many2many('stock.move', 'mrp_production_move_ids', 'production_id', 'move_id', 'Products IN', domain=[('state','!=', 'cancel')]),
        'move_all_dst_ids': fields.one2many('stock.move', 'production_id', 'Products OUT', domain=[('state','!=', 'cancel')]),
        'sale_requested_date': fields.function(_get_sale_dates, type='date', string='Requested date', multi='sale_dates', store=False),
        'sale_commitment_date': fields.function(_get_sale_dates, type='date', string='Commitment date', multi='sale_dates', store=False),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'partner_address_id': fields.many2one('res.partner.address', 'Address'),
        'partner_address_city_id': fields.related('partner_address_id', 'city_id', type='many2one', relation='city.city', string='City', store=True),
        'task_ids': fields.many2many('project.task', 'mrp_production_task_ids', 'production_id', 'task_id', 'Tasks', domain=[]),
        'tested_rate': fields.function(_get_tested, string='Tested', type='float', multi='tested', store=False),
        'tested_count': fields.function(_get_tested, string='Testing task count', type='float', multi='tested', store=False),
        'invalid_move_prod': fields.function(_get_invalid_move_prod, type='boolean', string='Invalid production move', store=True),
        'note': fields.text('Notes'),
    }
    
    def create(self, cr, uid, vals, context=None):
        procurement_obj = self.pool.get('procurement.order') 
        if vals.has_key('move_prod_id') and vals['move_prod_id'] != False:
            proc_ids = procurement_obj.search(cr, uid, [('move_id', '=', vals['move_prod_id'])], context=context)   
            for procurement in procurement_obj.browse(cr, uid, proc_ids, context):
                if procurement and procurement.sale_line_id:
                    vals['partner_id'] = procurement.sale_line_id.order_id and procurement.sale_line_id.order_id.partner_shipping_id.partner_id.id or False
                    vals['partner_address_id'] = procurement.sale_line_id.order_id and procurement.sale_line_id.order_id.partner_shipping_id.id or False,
                    break
                    
        return super(mrp_production, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
          ids = [ids]
          
        production_obj = self.pool.get('mrp.production')  
        procurement_obj = self.pool.get('procurement.order') 
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom') 
        product_obj = self.pool.get('product.product') 
        
        for production in production_obj.browse(cr, uid, ids, context):                               
            if vals.has_key('product_id'):
                for move in production.move_all_dst_ids:
                    if move.product_id.id <> vals['product_id']:
                        move_obj.write(cr, uid, [move.id], {'product_id': vals['product_id']}, context=context)
                        
                        # Update next move
                        if move.move_dest_id and move.move_dest_id.product_id.id == move.product_id.id:
                            move_obj.write(cr, uid, [move.move_dest_id.id],  {'product_id': vals['product_id']}, context=context)  

        return super(mrp_production, self).write(cr, uid, ids, vals, context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'date_start': False,
            'date_finished': False,
            'assigned_workcenter': False,
            'workcenter_lines' : [],
            'move_all_src_ids' : [],
            'move_all_dst_ids' : [],
            'partner_id' : False,
            'partner_address_id' : False
        })
        return super(mrp_production, self).copy(cr, uid, id, default, context)
    
    def run_picked_rate_scheduler(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}
        if not ids:
            ids = self.search(cr, uid, [('state', 'in', ('confirmed', 'picking_except', 'ready', 'in_production'))])

        for data in self.read(cr, uid, ids, ['picked_rate'], context=context): 
            vals = {'picked_rate': data['picked_rate'],}
            self.write(cr, uid, data['id'], vals, context=context)
    

    def action_produce(self, cr, uid, production_id, production_mode, context=None):

        stock_mov_obj = self.pool.get('stock.move')
        production = self.browse(cr, uid, production_id, context=context)
        
        if production_mode in ['consume','produce']:
            # Consume products (from the picking list to avoid consuming REF Manager moves)
            mrp_moves = []
            if production.picking_id:
                for move in production.picking_id.move_lines:
                    if move.move_dest_id: 
                        mrp_moves.append(move.move_dest_id)
                    else:
                        logging.getLogger('mrp.production').error('action_produce error, not move_dest %s: [%s] %s %s', move.name, move.product_id.default_code or '', move.product_id.name or '', move.picking_id and move.picking_id.name or '')
                
            #mrp_moves = [move.move_dest_id for move in production.picking_id.move_lines if production.picking_id]
            for move_consume in mrp_moves:
                logging.getLogger('mrp.production').info('action_produce on %s: [%s] %s %s', move_consume.name, move_consume.product_id.default_code or '', move_consume.product_id.name or '', move_consume.picking_id and move_consume.picking_id.name or '')
                move_consume.action_consume(move_consume.product_qty, move_consume.location_id.id, context=context)
                
            if production_mode == 'produce':
                # Create products
                for move_product in production.move_created_ids:
                    move_product.action_consume(move_product.product_qty, move_product.location_id.id, context=context)
                
            # Update all moves history
            for raw_product in production.move_lines2:
                new_parent_ids = []
                parent_move_ids = [x.id for x in raw_product.move_history_ids]
                for final_product in production.move_created_ids2:
                    if final_product.id not in parent_move_ids:
                        new_parent_ids.append(final_product.id)
                for new_parent_id in new_parent_ids:
                    stock_mov_obj.write(cr, uid, [raw_product.id], {'move_history_ids': [(4,new_parent_id)]})

        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'mrp.production', production_id, 'button_produce_done', cr)
        return True

    def button_create_task(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
          ids = [ids]
          
        result = {} 
        
        task_obj = self.pool.get('project.task')
        project_obj = self.pool.get('project.project')
        move_obj = self.pool.get('stock.move')
        proc_obj = self.pool.get('procurement.order')
        
        for production in self.browse(cr, uid, ids, context):
            
            procurement = False
            if production.move_prod_id:
                proc_ids = proc_obj.search(cr, uid, [('move_id', '=', production.move_prod_id.id)], context=context)   
                for procurement in proc_obj.browse(cr, uid, proc_ids, context):
                    break
                    
            project_ids = project_obj.search(cr, uid, [('name', 'ilike', 'test')], context=context) 
                
            data = {
                'name': production.product_id.name, 
                'notes': (_('Testing [%s] %s')) % (production.bom_id.name, production.product_id.name),
                'project_id': project_ids and project_ids[0] or False,
                'origin': ('%s:%s') % (production.origin, production.name),
                'date_deadline': production.date_planned,
                'planned_hours': 4.0,
                'remaining_hours': 4.0,
                'procurement_id': procurement and procurement.id or False, 
                'partner_id': production.partner_id and production.partner_id.id or False,
                'partner_address_id': production.partner_address_id and production.partner_address_id.id or False,
                'user_id': False,
                'company_id': production.company_id.id,
            }

            task_id = task_obj.create(cr, uid, data, context=context)
            production.write({'task_ids': [(4, task_id)]}, context=context)
            
            result[production.id] = task_id
            
        return result

mrp_production()


class mrp_production_workcenter_line(osv.osv):
    _name = 'mrp.production.workcenter.line'
    _inherit = 'mrp.production.workcenter.line'
    
    def _get_sequence(self, cr, uid, context={}):
        result = 0

        if context and 'production_id' in context:
            productions = self.pool.get('mrp.production').browse(cr, uid, context['production_id'])
            for line in productions.workcenter_lines:
                if line.sequence >= result:
                    result = line.sequence+1
            
        return int(time.time())

    _columns = {
        'name': fields.char('Work Order', size=300, required=True),
        'working_date': fields.date('Working Date', select=True, help="Date on which the work is done."),
    }
    _defaults = {
        'working_date': fields.date.context_today,
        'sequence': _get_sequence,
    }

mrp_production_workcenter_line()


class mrp_production_product_line(osv.osv):
    _name = 'mrp.production.product.line'
    _inherit = _name
    
    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Supplier'),
    }
    
mrp_production_product_line()
