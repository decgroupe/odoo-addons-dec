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

from osv import osv, fields

class invoice_custom_report(osv.TransientModel):
    _name = 'invoice.custom.report'
    _description = 'Customize invoice report'

    _columns = {
        'tax_summary': fields.boolean(
            'Print tax summary', 
            help="A table at end of the report will be displayed with the total amount per tax"
            ),
        'partner_bank_id': fields.many2one(
            'res.partner.bank', 
            'Bank Account',
                help='Bank Account Number to which the invoice will be paid. A Company bank account if this is a Customer Invoice or Supplier Refund, otherwise a Partner bank account number.', 
            ),
        }
    
    _defaults = {
        'tax_summary': True,
    }


    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        view_data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'account.invoice',
             'form': view_data,
        }
        res = {
            'type': 'ir.actions.report.xml',
            'datas': datas,
        }

        res['report_name'] = 'service_print_invoice'
        return res

invoice_custom_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: