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
    

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        result = super(ref_product,self).name_search(cr, user, name=name, args=args, operator=operator, context=context, limit=limit)
        
        # Make a specific search according to market reference
        ids = self.search(cr, user, [('ciel_code', '=', name),'|',('state', '!=', 'obsolete'),('state', '=', False)], limit=limit, context=context)
        if ids:
            res = []
            ciel_result = self.name_get(cr, user, ids, context=context)
            for item in ciel_result:
                item = list(item)
                item[1] = ('%s (%s)') % (item[1], name)
                res.append(item)
            result = res + result
                
        # Make a specific search to find a product with version inside
        if not result and 'V' in name:
            reference = name.rpartition('V')
            if reference[0]:
                res = []
                ids = self.search(cr, user, [('default_code', '=', reference[0])], limit=limit, context=context)
                res = self.name_get(cr, user, ids, context=context)
                result = res + result
            
        """
        # Search for obsolete products
        ids = [item[0] for item in result] 
        ids = self.search(cr, user, [('state', '=', 'obsolete'), ('id', 'in', ids)], limit=limit, context=context)
        if ids:
            for i, item in enumerate(result):
                if item[0] in ids: 
                    item = list(item)
                    item[1] = ('%s (OBSOLETE)') % (item[1])
                    result[i] = tuple(item) 
        """
            
        return result  
    
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
        res = []
        for key in keywords[0]: 
            if key and key[0] == '+':
                use_comments = True
                key = key[1:]
            else:
                use_comments = False
            
            if key:
                search_value = self.search(cr, uid, [('searchvalue', 'ilike', key)], context=context)
                search_category = self.search(cr, uid, [('category.name', 'ilike', key)], context=context)
                search_name = self.search(cr, uid, [('product.name', 'ilike', key)], context=context)
                search_ciel = self.search(cr, uid, [('product.ciel_code', '=', key)], context=context)
                
                if use_comments: 
                    search_comments = self.search(cr, uid, [('product.comments', 'ilike', key)], context=context)
                else:
                    search_comments = []    
                
                if len(key) >2:
                    search_tags = self.search(cr, uid, [('product.tagging_ids.name', 'ilike', key)], context=context)
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
                 
            ref_price = False   
            ref_price_ids = ref_price_obj.search(cr, uid, [('reference_id', '=', reference.id)], limit=1, context=context)
            if ref_price_ids:
                ref_price = ref_price_obj.browse(cr, uid, ref_price_ids, context=context)[0]
                
            if not ref_price or ref_price.value <> cost_price: 
                data['reference_id'] = reference.id
                data['value'] = cost_price
                ref_price_obj.create(cr, uid, data, context=context)
                if use_new_cursor:   
                    cr.commit()
            else:
                logging.getLogger('ref.reference').info('Price did not change for [%s] %s', reference.value, reference.product.name) 

        if use_new_cursor:
            cr.close()
        else:
            self.generate_material_cost_report(cr, uid, ids, context)
            
    def generate_material_cost_report(self, cr, uid, ids=None, date_ref1=False, date_ref2=False, context=None):
        if context is None:
            context = {}
            
        ref_price_obj = self.pool.get('ref.price')
        mail_message_obj = self.pool.get('mail.message')
        
        if not ids:
            ids = self.search(cr, uid, [])

        today = time.strftime('%Y-%m-%d')
        emailfrom = 'refmanager@dec-industrie.com'
        emails = ['decindustrie@gmail.com']
        subject = _('Price surcharge alert')
        body = ('%s\n\n') % (cr.dbname)        
        ref_content = []
          
        for reference in self.browse(cr, uid, ids, context=context): 
            ref1_ids = []
            ref2_ids = []
            if date_ref1:
                ref1_ids = ref_price_obj.search(cr, uid, [('reference_id','=', reference.id), ('date','<=', date_ref1)], limit=1)
            if date_ref2:
                ref2_ids = ref_price_obj.search(cr, uid, [('reference_id','=', reference.id), ('date','<=', date_ref2)], limit=1)
             
            if ref1_ids and ref2_ids:
                price_ids = ref2_ids + ref1_ids
            else:  
                price_ids = ref_price_obj.search(cr, uid, [('reference_id','=', reference.id)], limit=2)
                
            if (len(price_ids) >= 2):  
                prices = ref_price_obj.browse(cr, uid, price_ids, context=context)
                if (prices[0].value > prices[1].value) and (date_ref1 or date_ref2) or (prices[0].date == today): 
                    assert(prices[0].id == price_ids[0])
                    ref_content.append({'id': reference.id, 
                                       'reference': reference.value,
                                       'product': reference.product.name,
                                       'price0_date': prices[0].date,
                                       'price0_value': prices[0].value,
                                       'price1_date': prices[1].date,
                                       'price1_value': prices[1].value,
                                       'diff': prices[0].value - prices[1].value 
                                       })
                    
        ref_content = sorted(ref_content, key=lambda k: k['diff'], reverse=True)
        for content in ref_content:           
            body += ('[%s] %s - %d\n') % (content['reference'], content['product'], content['id'])
            body += ('%s:   %.2f\n') % (content['price1_date'], content['price1_value'])   
            body += ('%s:   %.2f (+%.2f)\n') % (content['price0_date'], content['price0_value'], content['price0_value']-content['price1_value'])   
            body += '\n'
          
        if ref_content:          
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


class ref_task_wizard(osv.osv_memory):
    _name = 'ref.task.wizard'

    def action_start_task(self, cr, uid, data, context):
        ref_reference_obj = self.pool.get('ref.reference')
        ref_price_obj = self.pool.get('ref.price') 
        
        
        #ref_reference_obj.run_material_cost_scheduler(cr, uid)
        
        # Remove duplicates
        ids = ref_reference_obj.search(cr, uid, [], context=context)
        for reference in ref_reference_obj.browse(cr, uid, ids, context=context):           
            price_ids = ref_price_obj.search(cr, uid, [('reference_id','=', reference.id)], context=context, order='date asc')
            if price_ids:
                price_ids_to_delete = []
                previous_price = False                
                for i, price in enumerate(ref_price_obj.browse(cr, uid, price_ids, context=context)):
                    assert(price_ids[i] == price.id)
                    if previous_price and price.value == previous_price.value:
                        #print 'Add %s to delete' % (price.date)
                        price_ids_to_delete.append(price.id)
                    previous_price = price
                    
                if price_ids_to_delete:
                    assert(len(price_ids_to_delete)<ids)
                    diff = [x for x in price_ids if x not in price_ids_to_delete]
                    ref_price_obj.unlink(cr, uid, price_ids_to_delete, context=context)
                    logging.getLogger('ref.task.wizard').info('Remaining ids %s for [%s] %s', diff, reference.value, reference.product.name) 
                  
        today = time.strftime('%Y-%m-%d')
        ref_reference_obj.generate_material_cost_report(cr, uid, ids, '2014-01-01', today, context=context)  
        #ref_reference_obj.generate_material_cost_report(cr, uid, ids, False, False, context=context)  
        
        return {}

ref_task_wizard()

