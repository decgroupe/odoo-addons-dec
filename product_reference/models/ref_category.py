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
