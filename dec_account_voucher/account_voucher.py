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


class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = _name
    
    _columns = {
        'property_account_journal': fields.property(
            'account.journal',
            type='many2one',
            relation='account.journal',
            domain=[('type','in',['bank','cash'])],
            string="Journal",
            view_load=True,
            help="This journal will be used instead of the default one for the current partner.",
        ),
    }


class account_voucher(osv.osv):
    _name = 'account.voucher' 
    _inherit = _name
    
    def onchange_journal_voucher(self, cr, uid, ids, line_ids=False, tax_id=False, price=0.0, partner_id=False, journal_id=False, ttype=False, company_id=False, context=None):
        """price
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        
        result = super(account_voucher, self).onchange_journal_voucher(cr, uid, ids, line_ids, tax_id, price, partner_id, journal_id, ttype, company_id, context)
        return result
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
        result = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)

        if partner_id:
            partner_obj = self.pool.get('res.partner')
            if not result.has_key('value'):
                result['value'] = {}
              
            partner = partner_obj.browse(cr, uid, partner_id, context=context)
            if partner.property_account_journal:
                result['value'].update({
                    'journal_id':partner.property_account_journal.id,
                })

        return result 
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

