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

class purchase_custom_report(osv.TransientModel):
    _name = 'purchase.custom.report'
    _description = 'Customize purchase report'

    _columns = {
            'total_amounts': fields.boolean('Total the amounts', help="Total the amounts for lines with same product, uom, unit price and notes"),
            'pack_print': fields.selection([('default','Default (by line setting)'), ('hide','Hide pack content'), ('show','Show full pack content')], 'Pack printing', size=16),
            'pack_hide_prices': fields.boolean('Hide pack line prices', help="Hide prices if equal to zero"),
        }
    
    _defaults = {
        'total_amounts': True,
        'pack_print': 'default',
    }

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        view_data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'purchase.order',
             'form': view_data,
        }
        res = {
            'type': 'ir.actions.report.xml',
            'datas': datas,
        }
        
        if context['report_type'] == 'quotation':
            res['report_name'] = 'service_print_purchase_quotation'
        elif context['report_type'] == 'order':
            res['report_name'] = 'service_print_purchase'
 
        return res

purchase_custom_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: