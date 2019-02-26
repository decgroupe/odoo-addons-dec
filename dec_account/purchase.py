# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010 Pexego S.L. (http://www.pexego.es) All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""
Extension of the purchase orders to add payment info.

Based on the sale_payment module.
"""


import netsvc
from osv import fields, osv

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def _get_default_payment_term(self, cr, uid, context=None):
        res = False
        partner_id = context and context.get('partner_id', False) or False
        partner_obj = self.pool.get('res.partner') 
        if partner_id:
            res = partner_obj.browse(cr, uid, partner_id).property_payment_term_supplier.id
            if not res:
                res = partner_obj.browse(cr, uid, partner_id).property_payment_term.id
                
        return res
    
    _columns = {
        'payment_term': fields.many2one('account.payment.term', 'Payment Term', help='The payment terms. They will be transferred to the invoice.'),
        'partner_bank': fields.many2one('res.partner.bank','Bank Account', select=True, help='The bank account to pay to or to be paid from. It will be transferred to the invoice.'),
    }
    
    _defaults = {
        #'payment_term': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').browse(cr, uid, context['partner_id']).property_payment_term_supplier.id,
        'payment_term': _get_default_payment_term,
    }
    

                
        

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        """
        Extends the onchange to set the payment info of the partner.
        """
        result = super(purchase_order, self).onchange_partner_id(cr, uid, ids, partner_id)
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            partner_payment_term_id = partner.property_payment_term_supplier and partner.property_payment_term_supplier.id or False
            if partner_payment_term_id:
                result['value']['payment_term'] = partner_payment_term_id
            else:
                partner_payment_term_id = partner.property_payment_term and partner.property_payment_term.id or False
                result['value']['payment_term'] = partner_payment_term_id
            

        return result


    def action_invoice_create(self, cr, uid, ids, context=None):
        """
        Extend the invoice creation action to preset the payment options.
        """
        # Create the invoice as usual.
        invoice_id = super(purchase_order, self).action_invoice_create(cr, uid, ids, context=context)

        #
        # Check if the order has payment info.
        #
        vals = {}
        for order in self.browse(cr, uid, ids):
            if order.payment_term:
                vals['payment_term'] = order.payment_term.id
            if order.partner_bank:
                vals['partner_bank_id'] = order.partner_bank.id
        if vals:
            # Write the payment info into the invoice.
            self.pool.get('account.invoice').write(cr, uid, [invoice_id], vals)
        return invoice_id

purchase_order()

