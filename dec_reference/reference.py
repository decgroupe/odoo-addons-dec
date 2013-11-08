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
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from tools.translate import _
import decimal_precision as dp
import time
import logging
import pooler



class ref_product(osv.osv):
    _inherit = "product.product"
    _name = _inherit

    _columns = {
        'ciel_code': fields.char('Ciel', size=24),
        'comments': fields.text('Comments'),
        'market_bom_id': fields.many2one('ref.market.bom', 'Market bill of materials and services'),
        'market_markup_rate': fields.float('Markup rate', help='Used by REF manager Market'), 
        'market_material_cost_factor': fields.float('Material factor (PF)', help='Used by REF manager Market'),     
    }
    
ref_product()


class ref_log(osv.osv):
    """ Reference log for all operations """

    _name = 'ref.log'
    _description = 'Log'
    _rec_name = 'operation'

    _columns = {
        'operation': fields.text('operation', required=True),
        'username': fields.text('username', required=True), 
        'localcomputername': fields.text('localcomputername', required=True),
        'localusername': fields.text('localusername', required=True),  
        'ipaddress': fields.text('ipaddress', required=True),   
        'datetime': fields.datetime('Modification date'),
    }

    _defaults = {
        'datetime': fields.datetime.now,
    }
    
    _order = 'id desc'

ref_log()



class ref_category(osv.osv):
    """ Description """

    _name = 'ref.category'
    _description = 'Category'
    _rec_name = 'name'

    _columns = {     
        'code': fields.char('Code', size=3, required=True),
        'name': fields.text('Name', required=True),
        'product_category': fields.many2one('product.category', 'Product category'),
        'description_template': fields.text('Template', required=False),
    }

    _defaults = {

    }
    
    _sql_constraints = [
       ('code_uniq', 'unique(code)', 'Code category must be unique !'),
    ] 


    _order = 'code'
    
    def name_get(self, cr, user, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]           
        if context is None:
            context = {}
        if not len(ids):
            return []
        
        result = []
        for category in self.browse(cr, user, ids, context=context):
            name =  ('%s: %s') % (category.code, category.name) 
            result.append((category.id, name))

        return result

ref_category()

class ref_property(osv.osv):
    """ Description """

    _name = 'ref.property'
    _description = 'Property'
    _rec_name = 'name'

    _columns = {     
        'name': fields.text('Name', required=True),
        'format': fields.text('Format', required=True),
        'fixed': fields.boolean('Fixed values'),
    }

    _defaults = {

    }
 
    _order = 'name'

ref_property()


class ref_category_line(osv.osv):
    """ Description """

    _name = 'ref.category.line'
    _description = 'Category line'
    _rec_name = 'description'

    _columns = {     
        'category': fields.many2one('ref.category', 'Category', required=True),
        'property': fields.many2one('ref.property', 'Property', required=True),
        'description': fields.char('Property description', size=128),
        'sequence': fields.integer('Position', required=True),
    }

    _defaults = {

    }
    
    _order = 'sequence'

ref_category_line()


class ref_market_category(osv.osv):
    """ Description """

    _name = 'ref.market.category'
    _description = 'Market Category'
    _rec_name = 'description'

    _columns = {     
        'prefix': fields.char('Prefix', size=6, required=True),
        'description': fields.char('Description', size=128, required=True),
        'sequence': fields.integer('Position', required=True),
    }

    _defaults = {

    }
    _order = 'sequence'
    

ref_market_category()


class ref_market_bom(osv.osv):

    _name = 'ref.market.bom'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_qty': fields.float('Product Qty', required=True, digits_compute=dp.get_precision('Product UoM')),
        'product_uom': fields.many2one('product.uom', 'Product UOM', required=True, help="UoM (Unit of Measure) is the unit of measurement for the inventory control"),
        'partner_id': fields.many2one('res.partner', 'Supplier'),
        'locked_price': fields.boolean('Locked price'),
        'price': fields.float('Price', digits_compute=dp.get_precision('Purchase Price')),
        'bom_lines': fields.one2many('ref.market.bom', 'bom_id', 'BoM Lines'),
        'bom_id': fields.many2one('ref.market.bom', 'Parent BoM', ondelete='cascade', select=True),
        'xml_id': fields.function(osv.osv.get_xml_id, type='char', size=128, string="External ID", help="ID of the view defined in xml file"),
        'create_date' : fields.datetime('Create Date', readonly=True),
        'create_uid' : fields.many2one('res.users', 'Creator', readonly=True),
        'write_date' : fields.datetime('Last Write Date', readonly=True),
        'write_uid' : fields.many2one('res.users', 'Last Writer', readonly=True),
    }
    
ref_market_bom()

class ref_attribute(osv.osv):
    """ Description """

    _name = 'ref.attribute'
    _description = 'Attribute'
    _rec_name = 'name'

    _columns = {     
        'owner': fields.many2one('ref.property', 'Owner', required=True),
        'value': fields.text('Value', required=True),
        'name': fields.text('Name', required=True),
    }

    _defaults = {

    }  
 
    _order = 'value'

ref_attribute()


class ref_price(osv.osv):
    """ Description """

    _name = 'ref.price'
    _description = 'Price'
    _columns = { 
        'reference_id': fields.many2one('ref.reference', 'Reference', ondelete='cascade', required=True),
        'date': fields.date('Date', required=True),   
        'value': fields.float('Price'),
    }
    
    _defaults = {
        'date': fields.datetime.now,
    }
    
    _order = 'date desc'

    def name_get(self, cr, uid, ids, context=None):
        result = []
        if ids:
            for price in self.browse(cr, uid, ids, context=context):
                result.append((r.id, ''))
            
        return result
        
ref_price()

class ref_reference(osv.osv):
    """ Description """

    _name = 'ref.reference'
    _description = 'Reference'
    _rec_name = 'value'

    _columns = {     
        'category': fields.many2one('ref.category', 'Category', required=True),
        'product': fields.many2one('product.product', 'Product', required=True),
        'product_ciel_code': fields.related('product', 'ciel_code', type='char', string='Ciel'),
        'product_ciel_code2': fields.related('product', 'ciel_code', type='char', string='Ciel', store={}),
        'product_name': fields.related('product', 'name', type='char', string='Name'),
        'product_state': fields.related('product', 'state', type='selection', string='Status'),
        'product_comments': fields.related('product', 'comments', type='text', string='Comments'),
        'current_version': fields.integer('Current version', required=True),
        'value': fields.text('Value', required=True),
        'searchvalue': fields.text('Search value', required=True),
        'datetime': fields.datetime('Create date', required=True),
        'folder_count': fields.integer('Product folder item count'),
        'folder_error': fields.integer('Product folder error count'),
        'folder_warning': fields.integer('Product folder warning count'),
        'folder_task': fields.integer('Product folder task count'),
        'picturepath': fields.text('Path to picture'),  
    }

    _defaults = {
        'datetime': fields.datetime.now,
    }
    
    _sql_constraints = [
       ('value_uniq', 'unique(value)', 'Reference value must be unique !'),
    ] 
    
    _order = 'value'
    

    def search_custom(self, cr, uid, keywords, context=None):
        ref_pool = self.pool.get('ref.reference')
        #product = self.browse
        #res = {}
        #res = ref_pool.search(cr, uid, [('product.tagging_ids.name','ilike',keywords)])
        #toto = keywords[0][0]

        res = []
        for key in keywords[0]:
            
            if key and key[0] == '+':
                use_comments = True
                key = key[1:]
            else:
                use_comments = False
            
            if key:
                search_value = ref_pool.search(cr, uid, [('searchvalue', 'ilike', key)])
                search_category = ref_pool.search(cr, uid, [('category.name', 'ilike', key)])
                search_name = ref_pool.search(cr, uid, [('product.name', 'ilike', key)])
                search_ciel = ref_pool.search(cr, uid, [('product.ciel_code', '=', key)])
                
                if use_comments: 
                    search_comments = ref_pool.search(cr, uid, [('product.comments', 'ilike', key)])
                else:
                    search_comments = []    
                
                if len(key) >2:
                    search_tags = ref_pool.search(cr, uid, [('product.tagging_ids.name', 'ilike', key)])
                else:
                    search_tags = []
                     
                res = res + search_value + search_category + search_name + search_comments + search_ciel + search_tags
        
        return res
    
    
    def run_material_cost_scheduler(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}

        mrp_bom_obj = self.pool.get('mrp.bom')
        ref_price_obj = self.pool.get('ref.price')

        use_new_cursor = False
        if use_new_cursor:
            cr = pooler.get_db(cr.dbname).cursor()
        
        if not ids:
            ids = self.search(cr, uid, [])
        for reference in self.browse(cr, uid, ids, context=context):
            data = {}
            cost_price = 0.0
            if reference.product and reference.product.bom_ids:
                bom_id = mrp_bom_obj._bom_find(cr, uid, reference.product.id, reference.product.uom_id and reference.product.uom_id.id, [])
                if bom_id:
                    logging.getLogger('ref.reference').info('Compute material cost price for [%s] %s', reference.value, reference.product.name)
                    cost_price = mrp_bom_obj.get_cost_price(cr, uid, [bom_id], context=context)[bom_id]
                    
            data['reference_id'] = reference.id
            data['value'] = cost_price
            ref_price_obj.create(cr, uid, data, context=context)
            if use_new_cursor:   
                cr.commit()

        if use_new_cursor:
            cr.close()
        else:
            self.generate_material_cost_report(cr, uid, ids, context)
            
    def generate_material_cost_report(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}
            
        ref_price_obj = self.pool.get('ref.price')
        mail_message_obj = self.pool.get('mail.message')
        
        if not ids:
            ids = self.search(cr, uid, [])

        emailfrom = 'refmanager@dec-industrie.com'
        emails = ['decindustrie@gmail.com']
        subject = _('Price surcharge alert')
        body = ('%s\n\n') % (cr.dbname)
        warn = False
          
        for reference in self.browse(cr, uid, ids, context=context):           
            price_ids = ref_price_obj.search(cr, uid, [('reference_id','=', reference.id)], limit=2)
            if (len(price_ids) >= 2):  
                prices = ref_price_obj.browse(cr, uid, price_ids, context=context)
                if prices[0].value > prices[1].value:   
                    warn = True                 
                    body += ('[%s] %s\n') % (reference.value, reference.product.name)
                    body += ('%s: %.2f\n') % (prices[0].date, prices[0].value)   
                    body += ('%s: %.2f (+%.2f)\n') % (prices[1].date, prices[1].value, prices[0].value-prices[1].value)   
                    body += '\n'
          
        if warn:          
            mail_message_obj.schedule_with_attach(cr, uid, emailfrom, emails, subject, body, model='ref.reference', reply_to=emailfrom)
            
ref_reference()

class ref_version(osv.osv):
    _name = 'ref.version'
    _description = 'Reference version'
    _columns = {
        'name': fields.char('Modification name', size=128, required=True),
        'version': fields.integer('Version', required=True),
        'datetime': fields.datetime('Modification date'),
        'author': fields.many2one('res.users', 'Author'),
        'reference': fields.many2one('ref.reference', 'Reference', select=True),
    }

    _defaults = {
        'author': lambda x, y, z, c: z,
        'datetime': fields.datetime.now,
    }

ref_version()

class ref_reference_line(osv.osv):
    """ Description """

    _name = 'ref.reference.line'
    _description = 'Reference line'
    _rec_name = 'value'

    _columns = {     
        'reference': fields.many2one('ref.reference', 'Reference', required=True),
        'property': fields.many2one('ref.property', 'Property', required=True),
        'attribute_id': fields.integer('Attribute'),
        'value': fields.text('Value'),
        'sequence': fields.integer('Position', required=True),
    }

    _defaults = {

    }
    
    _order = 'sequence'

ref_category_line()


class ref_pack(osv.osv):
    """ Description """

    _name = 'ref.pack'
    _description = 'Pack'
    _rec_name = 'product_name'

    _columns = {     
        'product': fields.many2one('product.product', 'Product', required=True),
        'name': fields.related('product', 'name', type='char', string='Name'),
        'default_code': fields.related('product', 'default_code', type='char', string='Code'),
        'ciel_code': fields.related('product', 'ciel_code', type='char', string='Ciel'),
        'type': fields.selection([('company','Company'),('manufacturer', 'Manufacturer')], 'Pack Type', required=True),
    }

ref_pack()


class taggings_ref_reference(osv.osv):
    _inherit = "tagging.tags"
    _name = _inherit

    _columns = {
        "reference_ids": fields.many2many("ref.reference", "tagging_ref_reference", "tag_id", "reference_id", string="References"),
        
    }
    
taggings_ref_reference()




class ref_reference_taggings(osv.osv):
    _inherit = "ref.reference"
    _name = _inherit

    _columns = {
        "tagging_ids": fields.many2many("tagging.tags", "tagging_ref_reference", "reference_id", "tag_id", string="Tags"),
        
    }
    
ref_reference_taggings()




class taggings_ref_attribute(osv.osv):
    _inherit = "tagging.tags"
    _name = _inherit

    _columns = {
        "attribute_ids": fields.many2many("ref.attribute", "tagging_ref_attribute", "tag_id", "attribute_id", string="Attributes"),
        
    }
    
taggings_ref_reference()


class ref_attribute_taggings(osv.osv):
    _inherit = "ref.attribute"
    _name = _inherit

    _columns = {
        "tagging_ids": fields.many2many("tagging.tags", "tagging_ref_attribute", "attribute_id", "tag_id", string="Tags"),
        
    }
ref_attribute_taggings()


