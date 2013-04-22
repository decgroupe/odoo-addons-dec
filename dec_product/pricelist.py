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
     
    # To avoid bug: "TypeError: dictionary key must be string"
    def price_get_multi_xmlrpc(self, cr, uid, pricelist_ids, products_by_qty_by_partner, context=None):  
        if context is None:
            context = {}
            
        multiprices = self.price_get_multi(cr, uid, pricelist_ids, products_by_qty_by_partner, context=context)
        
        result = []
        for product_id in multiprices:
            if type(product_id) == int:  
                prices = []
                for prices_by_pricelist in multiprices[product_id]:
                    if type(prices_by_pricelist) == int: 
                        res2 = {}
                        res2['pricelist_id'] = prices_by_pricelist
                        res2['pricelist_price'] = multiprices[product_id][prices_by_pricelist]
                        prices.append(res2)
                   
                res1 = {}     
                res1['product_id'] = product_id
                res1['prices'] = prices
                result.append(res1)

        return result
    

product_pricelist()
