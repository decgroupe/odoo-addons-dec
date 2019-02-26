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


class software_account(osv.osv):

    _name = 'software.account'
    _description = 'Software Account'
    _rec_name = 'login'

    _columns = {
        'supplier_id': fields.many2one('software.account.supplier', 'Supplier', required=True),
        'login': fields.char('Login', size=64, required=True),
        'password': fields.char('Password', size=64, required=True),
        'email': fields.char('E-Mail', size=64, required=True),
        'firstname': fields.char('Firstname', size=64),
        'lastname': fields.char('Lastname', size=64),
        'question': fields.text('Question'),
        'answer': fields.text('Answer'),
        'pin': fields.char('Pin Code', size=16),
        'product_id': fields.many2one('product.product', 'Product', domain=[], change_default=True),
        'production_id': fields.many2one('mrp.production', 'Production'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'datetime': fields.datetime('Modification date'),
        'info': fields.text('Informations'),
    }

    _defaults = {
        'datetime': fields.datetime.now,
    }
    
    _order = 'id desc'


software_account()


class software_account_supplier(osv.osv):

    _name = 'software.account.supplier'
    _description = 'Software Account supplier'

    _columns = {
        'name': fields.text('Name', required=True),
        'image': fields.binary('Image'),
        'rules': fields.text('Rules'),
    }

    _order = 'id desc'


software_account_supplier()
