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
    





# class taggings_ref_reference(osv.osv):
#     _inherit = "tagging.tags"
#     _name = _inherit

#     _columns = {
#         "reference_ids": fields.many2many("ref.reference", "tagging_ref_reference", "tag_id", "reference_id", string="References"),
        
#     }
    
# taggings_ref_reference()




# class ref_reference_taggings(osv.osv):
#     _inherit = "ref.reference"
#     _name = _inherit

#     _columns = {
#         "tagging_ids": fields.many2many("tagging.tags", "tagging_ref_reference", "reference_id", "tag_id", string="Tags"),
        
#     }
    
# ref_reference_taggings()




# class taggings_ref_attribute(osv.osv):
#     _inherit = "tagging.tags"
#     _name = _inherit

#     _columns = {
#         "attribute_ids": fields.many2many("ref.attribute", "tagging_ref_attribute", "tag_id", "attribute_id", string="Attributes"),
        
#     }
    
# taggings_ref_reference()


# class ref_attribute_taggings(osv.osv):
#     _inherit = "ref.attribute"
#     _name = _inherit

#     _columns = {
#         "tagging_ids": fields.many2many("tagging.tags", "tagging_ref_attribute", "attribute_id", "tag_id", string="Tags"),
        
#     }
# ref_attribute_taggings()


# class ref_task_wizard(osv.osv_memory):
#     _name = 'ref.task.wizard'

#     def action_start_task(self, cr, uid, data, context):
#         ref_reference_obj = self.pool.get('ref.reference')
#         ref_price_obj = self.pool.get('ref.price') 
        
        
#         #ref_reference_obj.run_material_cost_scheduler(cr, uid)
        
#         # Remove duplicates
#         ids = ref_reference_obj.search(cr, uid, [], context=context)

#         for reference in ref_reference_obj.browse(cr, uid, ids, context=context):           
#             price_ids = ref_price_obj.search(cr, uid, [('reference_id','=', reference.id)], context=context, order='date asc')
#             if price_ids:
#                 price_ids_to_delete = []
#                 previous_price = False                
#                 for i, price in enumerate(ref_price_obj.browse(cr, uid, price_ids, context=context)):
#                     assert(price_ids[i] == price.id)
#                     if previous_price and price.value == previous_price.value:
#                         #print 'Add %s to delete' % (price.date)
#                         price_ids_to_delete.append(price.id)
#                     previous_price = price
                    
#                 if price_ids_to_delete:
#                     assert(len(price_ids_to_delete)<ids)
#                     diff = [x for x in price_ids if x not in price_ids_to_delete]
#                     ref_price_obj.unlink(cr, uid, price_ids_to_delete, context=context)
#                     logging.getLogger('ref.task.wizard').info('Remaining ids %s for [%s] %s', diff, reference.value, reference.product.name) 
         
#         today = time.strftime('%Y-%m-%d')
#         ref_reference_obj.generate_material_cost_report(cr, uid, ids, '2014-01-01', today, context=context)  
#         #ref_reference_obj.generate_material_cost_report(cr, uid, ids, False, False, context=context) 
        
#         #ref_reference_obj.run_material_cost_scheduler(cr, uid, context=context) 
        
#         return {}

# ref_task_wizard()

