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


class licence_licence(osv.osv):
    """ Reference log for all operations """

    _name = 'licence.licence'
    _description = 'Licence'
    _rec_name = 'serial'

    _columns = {
        'serial': fields.char('Serial', size=64, required=True),
        'application_id': fields.many2one('licence.application', 'Application', required=True),
        'dongle_id': fields.integer('Dongle ID'),
        'dongle_product_id': fields.integer('Dongle Product ID'),
        'dongle_id_encrypted': fields.char('Dongle ID Encrypted', size=64),
        'classic': fields.boolean('System Classic'),
        'cave': fields.boolean('System Cave'),
        'rift': fields.boolean('System Rift'),
        'vive': fields.boolean('System Vive'),
        'product_id': fields.many2one('product.product', 'Product', domain=[], change_default=True),
        'production_id': fields.many2one('mrp.production', 'Production'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'datetime': fields.datetime('Modification Date'),
        'info': fields.text('Informations'),
    }

    _defaults = {
        'datetime': fields.datetime.now,
    }
    
    _order = 'id desc'

licence_licence()

class licence_application(osv.osv):
    """ Reference log for all operations """

    _name = 'licence.application'
    _description = 'Licence application'

    _columns = {
        'application_id': fields.integer('ID', required=True), 
        'dongle_product_id': fields.integer('Dongle Product ID', help='Product ID to write into the dongle'),
        'name': fields.text('Application', required=True),
        'info': fields.text('Informations'),
    }
    
    _order = 'application_id asc, name'

    _defaults = {
        'application_id': 0,
    }


licence_application()
