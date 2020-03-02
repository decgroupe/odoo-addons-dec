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
