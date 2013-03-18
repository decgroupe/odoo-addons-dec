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

import time

from osv import fields
from osv import osv

class product_category(osv.osv):

    _name = "product.category"
    _inherit = _name
    _columns = {
        'xml_id': fields.function(osv.osv.get_xml_id, type='char', size=128, string="External ID", help="ID of the view defined in xml file"),
    }
    
    
class product_product(osv.osv):
    _name = "product.product.extended"
    _inherit="product.product"
    
    
    def _default_supplier_price(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        
        for product in self.browse(cr, uid, ids, context=context):     
            if product.seller_id:
                pricelist = product.seller_id.property_product_pricelist_purchase
                if pricelist:
                    pricelist_pool = self.pool.get('product.pricelist')
                    price = pricelist_pool.price_get(cr,uid,[pricelist.id], product.id, 1.0, product.seller_id.id, {
                            'uom': product.uom_po_id.id,
                            'date': time.strftime('%Y-%m-%d'),
                            })[pricelist.id]
            else:
                price = product.standard_price
                
            res[product.id] = price

        return res

    
    _columns = {
    'default_supplier_price': fields.function(_default_supplier_price, string='Default supplier price'),
    }
    
product_product()


class product_product(osv.osv):
    _name = 'product.product'
    _inherit = _name
    
    
    def _default_supplier_code(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
            
        for product in self.browse(cr, uid, ids, context=context):    
            if product.seller_info_id and product.seller_info_id.product_code:
                res[product.id] = product.seller_info_id.product_code
            else:
                res[product.id] = False;

        return res

    
    _columns = {
#        'move_lines': fields.one2many('stock.move', 'product_id', 'Product moves'),
        'supplier_code': fields.function(_default_supplier_code, type='char', string='Supplier code', store=True),        
        'xml_id': fields.function(osv.osv.get_xml_id, type='char', size=128, string="External ID", help="ID of the view defined in xml file"),
        'create_date' : fields.datetime('Create Date', readonly=True),
        'create_uid' : fields.many2one('res.users', 'Creator', readonly=True),
        'write_date' : fields.datetime('Last Write Date', readonly=True),
        'write_uid' : fields.many2one('res.users', 'Last Writer', readonly=True),
    }

    def get_product_available_xmlrpc(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        #context['states'] = ('confirmed','waiting','assigned','done')
        #context['what'] = ('in','out')
            
        res = self.get_product_available(cr, uid, ids, context=context)
    
        if type(res) == dict:
            res2 = {}
            for key in res:
                data = res[key] 
                if type(data) != dict:
                    res2[str(key)] = res[key] # Return only by product ID
            return res2
        return res
        
    

product_product()
