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

class voucher_custom_report(osv.TransientModel):
    _name = 'voucher.custom.report'
    _description = 'Customize voucher report'

    _columns = {
        'should_print_debit_lines': fields.boolean(
            'Print debit lines', 
            help=""
            ),
        'should_print_debit_line_at_0': fields.boolean(
            'Print debit lines with an amount of zero', 
            help=""
            ),
        'should_print_credit_lines': fields.boolean(
            'Print credit lines', 
            help=""
            ),
        'should_print_credit_line_at_0': fields.boolean(
            'Print credit lines with an amount of zero', 
            help=""
            ),
    }
    
    _defaults = {
        'should_print_debit_lines': True,
        'should_print_debit_line_at_0': True,
        'should_print_credit_lines': True,
        'should_print_credit_line_at_0': True,
    }

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        view_data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'account.voucher',
             'form': view_data,
        }
        res = {
            'type': 'ir.actions.report.xml',
            'datas': datas,
        }

        res['report_name'] = 'service_print_voucher'
        return res

voucher_custom_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: