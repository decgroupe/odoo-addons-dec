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

class account_move_line(osv.osv):
    _name = "account.move.line"   
    _inherit = _name

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        result = []
        
        for line in self.browse(cr, uid, ids, context=context):
            name_title = ''
            if line.ref:
                name_title = (line.id, (line.move_id.name or '') +' ('+line.ref+')'+ ' [' + (line.invoice.company_invoice_number or '') +']') 
            else:
                name_title = (line.id, line.move_id.name)
            result.append(name_title)
        return result