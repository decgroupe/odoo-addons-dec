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


import netsvc
from osv import fields, osv


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
                                group=False, type='out_invoice', context=None):
        """
        Extend the invoice creation action to set the price type if needed.
        """
        # Create the invoices as usual-
        res = super(stock_picking, self).action_invoice_create(cr, uid, ids,
                    journal_id=journal_id, group=group, type=type, context=context)

        for picking_id, invoice_id in res.items():
            picking = self.browse(cr, uid, picking_id, context=context)

            # Check if the picking comes from a purchase
            if picking.purchase_id:
                # Use the payment options from the order
                order = picking.purchase_id
                vals = {}
                if order.payment_term:
                    vals['payment_term'] = order.payment_term.id
                if order.partner_bank:
                    vals['partner_bank_id'] = order.partner_bank.id
                if vals:
                    # Write the payment info into the invoice.
                    self.pool.get('account.invoice').write(cr, uid, [invoice_id], vals, context=context)
                    
        return res

stock_picking()

