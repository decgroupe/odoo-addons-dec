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
import decimal_precision as dp

class account_invoice(osv.osv):
    
    
    def _get_client_order_ref(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        sale_order_obj = self.pool.get('sale.order')    
        
        for invoice in self.browse(cr, uid, ids, context=context): 
            res[invoice.id] = invoice.origin or '' 
            sale_order_ids = sale_order_obj.search(cr, uid, [('name', '=', invoice.origin)], context=context)   
            for order in sale_order_obj.browse(cr, uid, sale_order_ids, context=context):    
                if order.client_order_ref:
                    res[invoice.id] = res[invoice.id] + ' ' + order.client_order_ref;

        return res
    
    _inherit = "account.invoice"
    _columns = {
        'client_order_ref': fields.function(_get_client_order_ref, type='char', string='Customer Reference'),
    }

account_invoice()


class account_invoice_line(osv.osv):
 

    def _discount_price(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            quantity = 1.0 if line.quantity > 0 else 0.0
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, quantity, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

    _inherit = "account.invoice.line"
    _columns = {
        'price_discount': fields.function(_discount_price, string='Unit Price (discount)', digits_compute= dp.get_precision('Account')),
    }
    
account_invoice_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
