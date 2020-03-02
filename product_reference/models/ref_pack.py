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
        'list_price': fields.related('product', 'list_price', type='float', string='Sale Price'),
        'standard_price': fields.related('product', 'standard_price', type='float', string='Cost Price'),
        'type': fields.selection([('company','Company'),('manufacturer', 'Manufacturer')], 'Pack Type', required=True),
    }
