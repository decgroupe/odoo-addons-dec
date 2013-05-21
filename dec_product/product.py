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
    
class product_template(osv.osv):
    _name = "product.template"
    _inherit = _name

    PRODUCT_STATE = [
        ('',''),
        ('draft','In Development'),
        ('review', 'Need review'),
        ('sellable', 'Normal'),
        ('end','End of Lifecycle'),
        ('obsolete','Obsolete'),
    ] 
    
    _columns = {
        'state': fields.selection(PRODUCT_STATE, 'Status', help="Tells the user if he can use the product or not."),
    }

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
    
    
    def _default_purchase_price(self, cr, uid, ids, field_name, arg, context=None):
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
    
    def _default_sell_price(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}

        pricelist_pool = self.pool.get('product.pricelist')
        for product in self.browse(cr, uid, ids, context=context):     
            if product.company_id and product.company_id.partner_id:
                pricelist = product.company_id.partner_id.property_product_pricelist
                if pricelist:
                    price = pricelist_pool.price_get(cr,uid,[pricelist.id], product.id, 1.0, product.seller_id.id, {
                            'uom': product.uom_po_id.id,
                            'date': time.strftime('%Y-%m-%d'),
                            })[pricelist.id]
            else:
                price = product.list_price
                
            res[product.id] = price

        return res
    
    _columns = {
        'default_purchase_price': fields.function(_default_purchase_price, string='Purchase price', help="Purchase price based on default seller pricelist"),   
        'default_sell_price': fields.function(_default_sell_price, string='Sell price', help="Sell price based on default sell pricelist"),     
        'supplier_code': fields.function(_default_supplier_code, type='char', string='Supplier code', store=True),        
        'xml_id': fields.function(osv.osv.get_xml_id, type='char', size=128, string="External ID", help="ID of the view defined in xml file"),
        'create_date' : fields.datetime('Create Date', readonly=True),
        'create_uid' : fields.many2one('res.users', 'Creator', readonly=True),
        'write_date' : fields.datetime('Last Write Date', readonly=True),
        'write_uid' : fields.many2one('res.users', 'Last Writer', readonly=True),
           
        'pricelist_bypass': fields.boolean('By-pass', help="A bypass action will create a pricelist item to overwrite pricelist computation"),
#        'pricelist_item_id': fields.many2one('product.pricelist.item', 'Net price item', domain="[('product_id','=',active_id)]"), 
#        'pricelist_surcharge':  fields.related('pricelist_item_id', 'price_surcharge', type="float", string="Net price value", store=False),
        'price_write_date' : fields.datetime('Price write date'),
        'price_write_uid' : fields.many2one('res.users', 'Price last editor'),
    }
    

    def write(self, cr, uid, ids, vals, context=None):
        if not vals:
            vals= {}
            
        if 'standard_price' in vals:
            vals['price_write_date'] = time.strftime('%Y-%m-%d')
            vals['price_write_uid'] = uid
            
            
        if 'pricelist_bypass' in vals:
            if vals['pricelist_bypass']:
                pass
            else:
                pass
        
        result = super(product_product,self).write(cr, uid, ids, vals, context)
        return result

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
        
