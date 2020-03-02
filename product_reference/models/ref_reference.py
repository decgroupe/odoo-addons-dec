# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Mar 2020

import time

from osv import fields
from osv import osv
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from tools.translate import _
import decimal_precision as dp
import time
import logging
import pooler

log = logging.getLogger('ref.reference')

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
            #ids = [126,556]
        for reference in self.browse(cr, uid, ids, context=context):
            if reference.category.code in ['ADT']:
                continue
            #log.info("Reference category name is {0}".format(reference.category.name))
            data = {}
            cost_price = 0.0
            if reference.product and reference.product.bom_ids:
                bom_id = mrp_bom_obj._bom_find(cr, uid, reference.product.id, reference.product.uom_id and reference.product.uom_id.id, [])
                if bom_id:
                    logging.getLogger('ref.reference').info('Compute material cost price for [%s] %s', reference.value, reference.product.name)
                    try:
                        cost_price = mrp_bom_obj.get_cost_price(cr, uid, [bom_id], context=context)[bom_id]
                    except Exception, e:
                        logging.getLogger('ref.reference').exception("Failed to get cost price for [%s] %s\n %s", reference.value, reference.product.name, tools.ustr(e))

            ref_price = False   
            ref_price_ids = ref_price_obj.search(cr, uid, [('reference_id', '=', reference.id)], limit=1, context=context)
            if ref_price_ids:
                ref_price = ref_price_obj.browse(cr, uid, ref_price_ids, context=context)[0]
                
            if not ref_price or round(ref_price.value,2) <> round(cost_price,2): #abs(ref_price.value - cost_price) > 0.1
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
            self.generate_material_cost_report(cr, uid, ids, context=context)
            
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
            if reference.category.name in ['ADT']:
                continue
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
                if (round(prices[0].value,2) > round(prices[1].value,2)) and ((date_ref1 or date_ref2) or (prices[0].date == today)): 
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
