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

import time
from tools.translate import _
import decimal_precision as dp


class product_pricelist(osv.osv):
    _name = "product.pricelist"
    _inherit = _name
    
    # To avoid bug: "TypeError: dictionary key must be string"
    def price_get_xmlrpc(self, cr, uid, ids, prod_id, qty, partner=None, context=None):  
        if context is None:
            context = {}
            
        res = self.price_get(cr, uid, ids, prod_id, qty, partner, context=context)
    
        if type(res) == dict:
            res2 = {}
            for key in res:
                data = res[key] 
                if type(data) != dict:
                    res2[str(prod_id)] = res[key] # Return price only by product ID
                    #res2[str(key)] = res[key]
            return res2
        return res
    

product_pricelist()
