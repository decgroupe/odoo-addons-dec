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
    
    _columns = {
	    'code': fields.char('Reference', size=64),
        'landmark': fields.char('Landmark', size=64),
        'partner_id': fields.many2one('res.partner', 'Supplier'),
    }

mrp_bom()


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
        location_id = production.location_src_id.id
        date_planned = production.date_planned
        procurement_name = (production.origin or '').split(':')[0] + ':' + production.name
        
        procurement_fields = {
                    'name': procurement_name,
                    'origin': procurement_name,
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
            
            alt_moves = []
            for move in prod.move_lines:
                total_count += 1
                if move.state in ('assigned'):
                    ready_count += 1
                elif move.state in ('waiting'):
                    alt_moves += [move.id]
                    
            for move in prod.move_lines2:
                if move.state in ('done'):
                    total_count += 1
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
    
    def _get_view_name(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
             
        for prod in self.browse(cr, uid, ids, context=context):
            res[prod.id] = '%s: %s (%s)' % (prod.name, prod.product_id.name, prod.bom_id.name)  
            
        return res  

    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True, readonly=False, states={'draft':[('readonly',False)]}),
        'bom_id': fields.many2one('mrp.bom', 'Bill of Material', domain=[('bom_id','=',False)], required=True, readonly=False, states={'draft':[('readonly',False)]}),
        'duration': fields.float('Duration'),
        'date_start': fields.date('Start Date', select=True),
        'date_finished': fields.date('End Date', select=True),
        'assigned_workcenter': fields.many2one('mrp.workcenter', 'Assigned to', required=False),
        'late': fields.function(_get_late, type='boolean', string='Late', store=True),
        'sale_requested_date': fields.function(_get_sale_dates, type='date', string='Requested date', multi='sale_dates', store=False),
        'sale_commitment_date': fields.function(_get_sale_dates, type='date', string='Commitment date', multi='sale_dates', store=False),
        'view_name': fields.function(_get_view_name, string='View name', type='char'), 
        'picked_rate': fields.function(_picked_rate, string='Picked', type='float'),
#        , store={
#                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['picking_id'], 20),
#                'mrp.production': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
#                'mrp.production': (lambda self, cr, uid, ids, c={}: ids, ['move_lines2'], 20),
#                }),
    }

    def write(self, cr, uid, ids, vals, context=None):
        
        procurement_obj = self.pool.get('procurement.order') 
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom') 
        product_obj = self.pool.get('product.product') 
        
        for prod in self.browse(cr, uid, ids, context):
            if vals.has_key('product_id'):
                for move in prod.move_created_ids:
                    if move.product_id.id <> vals['product_id']:
                        move_obj.write(cr, uid, [move.id], {'product_id': vals['product_id']}, context=context)
                        
                        # Update next move
                        if move.move_dest_id and move.move_dest_id.product_id.id == move.product_id.id:
                            move_obj.write(cr, uid, [move.move_dest_id.id],  {'product_id': vals['product_id']}, context=context)           

        return super(mrp_production, self).write(cr, uid, ids, vals, context)

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
