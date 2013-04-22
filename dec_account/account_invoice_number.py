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

from osv import fields, osv
from tools.translate import _

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        'origin': fields.char('Source Document', size=300, help="Reference of the document that produced this invoice.", readonly=True, states={'draft':[('readonly',False)]}),
        'company_invoice_number': fields.char('Company invoice number', size=64, readonly=False, states={'draft':[('readonly',False)]}),
    }
    
    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        sale_order_obj = self.pool.get('sale.order')
        purchase_order_obj = self.pool.get('purchase.order')
        SUPER_ADMIN = 1
        
        res = super(account_invoice, self).unlink(cr, uid, ids, context=context)
        
        if uid <> SUPER_ADMIN:   
            for invoice in self.browse(cr, uid, ids, context=context):  
                
                sale_ids = sale_order_obj.search(cr, uid, [('invoice_ids','=',invoice.id)], context=context)
                if len(sale_ids) > 0:   
                    raise osv.except_osv(_('Invalid action !'), _('You cannot delete an invoice linked to a sale order.'))
                
                purchase_ids = purchase_order_obj.search(cr, uid, [('invoice_ids','=',invoice.id)], context=context)
                if len(purchase_ids) > 0:   
                    raise osv.except_osv(_('Invalid action !'), _('You cannot delete an invoice linked to a purchase order.'))

        return res
    
account_invoice()

    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

