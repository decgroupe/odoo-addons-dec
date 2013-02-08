# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP SA (<http://openerp.com>).
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
from osv import fields, osv
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from tools.float_utils import float_compare
import decimal_precision as dp
from tools.translate import _

class stock_partial_picking_line(osv.TransientModel):
    _name = "stock.partial.picking.line"
    _inherit = _name

    _columns = {
        'expected_quantity' : fields.float("Expected", digits_compute=dp.get_precision('Product UoM')),
        'move_origin': fields.related('move_id', 'move_origin', type='char', string='Move origin'),
        'move_final_location': fields.related('move_id', 'move_final_location', type='char', string='Final location'),
    }

class stock_partial_picking(osv.osv_memory):
    _name = "stock.partial.picking"
    _inherit = _name
    
    def _partial_move_for(self, cr, uid, move):
#        partial_move = {
#            'product_id' : move.product_id.id,
#            'quantity' : 0,#move.state in ('assigned','draft') and move.product_qty or 0,
#            'expected_quantity' : move.state in ('assigned','draft') and move.product_qty or 0,
#            'product_uom' : move.product_uom.id,
#            'prodlot_id' : move.prodlot_id.id,
#            'move_id' : move.id,
#            'location_id' : move.location_id.id,
#            'location_dest_id' : move.location_dest_id.id,
#        }
#        if move.picking_id.type == 'in' and move.product_id.cost_method == 'average':
#            partial_move.update(update_cost=True, **self._product_cost_for_average_update(cr, uid, move))
#        
        partial_move = super(stock_partial_picking, self)._partial_move_for(cr, uid, move)
        partial_move['expected_quantity'] = partial_move['quantity']
        partial_move['quantity'] = 0
        
        return partial_move
    

    def do_partial(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time'
        partial = self.browse(cr, uid, ids[0], context=context)
        
        sum_quantity = 0
        for wizard_line in partial.move_ids:
            if wizard_line.quantity >= 0:
                sum_quantity += wizard_line.quantity
            
        if sum_quantity == 0:
            raise osv.except_osv(_('Warning!'), _('Please provide Proper Quantity !'))

        return super(stock_partial_picking, self).do_partial(cr, uid, ids, context)
