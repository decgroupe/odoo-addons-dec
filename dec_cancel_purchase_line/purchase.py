# -*- coding: utf-8 -*-
##############################################################################
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

import netsvc

from osv import fields
from osv.orm import Model
from osv.orm import browse_record, browse_null
from tools.translate import _


class purchase_order_line(Model):

    _inherit = 'purchase.order.line'

    _columns = {
        'origin_procurement_order_id': fields.many2one('procurement.order', 'Procurement'),         
        'merge_origin': fields.char('Merge source', size=64),
    }

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        procurement_ids = []
        for line in self.browse(cr, uid, ids, context):
            if line.origin_procurement_order_id:
                procurement_ids.append(line.origin_procurement_order_id.id)
        self.pool.get('procurement.order').action_cancel(cr, uid, procurement_ids)
        return super(purchase_order_line, self).unlink(cr, uid, ids, context)

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
          ids = [ids]
        
        procurement_obj = self.pool.get('procurement.order') 
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom') 
        product_obj = self.pool.get('product.product') 
        
        for line in self.browse(cr, uid, ids, context):
            # Edit procurement product data
            if line.origin_procurement_order_id:
        
                note = ''
                product_data = {}
                if vals.has_key('product_id') and vals['product_id'] <> line.origin_procurement_order_id.product_id.id:
                    product_data['product_id'] = vals['product_id']
                    products = product_obj.browse(cr, uid, [line.origin_procurement_order_id.product_id.id, product_data['product_id']], context=context)  
                    note += _('PO/Switching product from:\n  -[%s] %s\n to\n  -[%s] %s\n') % (products[0].default_code, products[0].name, products[1].default_code, products[1].name)
                    
                if vals.has_key('product_uom') and vals['product_uom'] <> line.origin_procurement_order_id.product_uom.id:
                    product_data['product_uom'] = vals['product_uom']
                    uoms = uom_obj.browse(cr, uid, [line.origin_procurement_order_id.product_uom.id, product_data['product_uom']], context=context)  
                    note += _('PO/Switching uom from: %s to %s\n') % (uoms[0].name, uoms[1].name)
                    
                if vals.has_key('product_qty') and vals['product_qty'] <> line.origin_procurement_order_id.product_qty:
                    product_data['product_qty'] = vals['product_qty']
                    note += _('PO/Switching quantity from: %s to %s\n') % (line.origin_procurement_order_id.product_qty, product_data['product_qty'])
                 
                if product_data:
                    
                    if line.origin_procurement_order_id.note:
                        product_data['note'] = line.origin_procurement_order_id.note + '\n' + note
                    else:
                        product_data['note'] = note
                
                    procurement_obj.write(cr, uid, [line.origin_procurement_order_id.id], product_data, context=context)
                    # Update existing move in procurement
                    if line.origin_procurement_order_id.move_id and line.origin_procurement_order_id.move_id.product_id.id == line.origin_procurement_order_id.product_id.id:
                        move_obj.write(cr, uid, [line.origin_procurement_order_id.move_id.id], product_data, context=context)
                        # Update next move
                        if line.origin_procurement_order_id.move_id.move_dest_id and line.origin_procurement_order_id.move_id.move_dest_id.product_id.id == line.origin_procurement_order_id.product_id.id:
                            move_obj.write(cr, uid, [line.origin_procurement_order_id.move_id.move_dest_id.id], product_data, context=context)

        return super(purchase_order_line, self).write(cr, uid, ids, vals, context)


class purchase_order(Model):

    _inherit = 'purchase.order'

    def do_merge(self, cr, uid, ids, context=None):
        """
        To merge similar type of purchase orders.
        Orders will only be merged if:
        * Purchase Orders are in draft
        * Purchase Orders belong to the same partner
        * Purchase Orders are have same stock location, same pricelist
        Lines will only be merged if:
        * Order lines are exactly the same except for the quantity and unit

         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: the ID or list of IDs
         @param context: A standard dictionary

         @return: new purchase order id

        """
        #TOFIX: merged order line should be unlink
        wf_service = netsvc.LocalService("workflow")
        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id', 'move_dest_id', 'account_analytic_id'):
                    if not field_val:
                        field_val = False
                if isinstance(field_val, browse_record):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif isinstance(field_val, list):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

    # compute what the new orders should contain

        new_orders = {}
        for porder in [order for order in self.browse(cr, uid, ids, context=context) if order.state == 'draft']:
            order_key = make_key(porder, ('partner_id', 'location_id', 'pricelist_id'))
            new_order = new_orders.setdefault(order_key, ({}, []))
            new_order[1].append(porder.id)
            order_infos = new_order[0]
            if not order_infos:
                order_infos.update({
                    'origin': porder.origin,
                    'date_order': porder.date_order,
                    'partner_id': porder.partner_id.id,
                    'partner_address_id': porder.partner_address_id.id,
                    'dest_address_id': porder.dest_address_id.id,
                    'warehouse_id': porder.warehouse_id.id,
                    'location_id': porder.location_id.id,
                    'pricelist_id': porder.pricelist_id.id,
                    'state': 'draft',
                    'order_line': {},
                    'notes': '%s' % (porder.notes or '',),
                    'fiscal_position': porder.fiscal_position and porder.fiscal_position.id or False,
                })
            else:
                if porder.date_order < order_infos['date_order']:
                    order_infos['date_order'] = porder.date_order
                if porder.notes:
                    order_infos['notes'] = (order_infos['notes'] or '') + ('\n%s' % (porder.notes,))
                if porder.origin:
                    if not porder.origin in order_infos['origin'] and not order_infos['origin'] in porder.origin: # Do not add duplicates origin, totally useless
                        order_infos['origin'] = (order_infos['origin'] or '') + ' ' + porder.origin

            for order_line in porder.order_line:
                order_line.merge_origin = porder.origin 
                line_key = make_key(order_line, ('name', 'date_planned', 'taxes_id', 'price_unit', 'notes', 'product_id', 'move_dest_id', 'account_analytic_id', 'origin_procurement_order_id', 'merge_origin'))
                o_line = order_infos['order_line'].setdefault(line_key, {})
                
                if o_line:
                    # merge the line with an existing line
                    o_line['product_qty'] += order_line.product_qty * order_line.product_uom.factor / o_line['uom_factor']
                else:
                    # append a new "standalone" line
                    for field in ('product_qty', 'product_uom'):
                        field_val = getattr(order_line, field)
                        if isinstance(field_val, browse_record):
                            field_val = field_val.id
                        o_line[field] = field_val
                    o_line['uom_factor'] = order_line.product_uom and order_line.product_uom.factor or 1.0
                    o_line['origin_procurement_order_id'] = order_line.origin_procurement_order_id and order_line.origin_procurement_order_id.id or False
                    o_line['merge_origin'] = order_infos['origin'] or False  


        allorders = []
        orders_info = {}
        for order_key, (order_data, old_ids) in new_orders.iteritems():
            # skip merges with only one order
            if len(old_ids) < 2:
                allorders += (old_ids or [])
                continue

            # cleanup order line data
            for key, value in order_data['order_line'].iteritems():
                del value['uom_factor']
                value.update(dict(key))
            order_data['order_line'] = [(0, 0, value) for value in order_data['order_line'].itervalues()]

            # create the new order
            neworder_id = self.create(cr, uid, order_data)
            orders_info.update({neworder_id: old_ids})
            allorders.append(neworder_id)

            po_line_obj = self.pool.get('purchase.order.line')


            # remove the origin procurement link from the old lines
            # it has been assigned to the new po line
            old_line_ids = po_line_obj.search(
                cr, uid,
                [('order_id', 'in', old_ids),
                 ('origin_procurement_order_id', '!=', False)],
                context=context)

            po_line_obj.write(
                cr, uid, old_line_ids, {'origin_procurement_order_id': False}, context=context)

            # make triggers pointing to the old orders point to the new order
            for old_id in old_ids:
                wf_service.trg_redirect(uid, 'purchase.order', old_id, neworder_id, cr)
                wf_service.trg_validate(uid, 'purchase.order', old_id, 'purchase_cancel', cr)
        return orders_info

