# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from lxml import etree
import time
from datetime import datetime, date

from tools.translate import _
from osv import fields, osv
from openerp.addons.resource.faces import task as Task

class task(osv.osv):
    _name = "project.task"
    _inherit = _name
    
    
    def _get_sale_dates(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
        
        for id in ids:
            res[id] = {}.fromkeys(field_names, False)
         
        SUPER_USER = 1   
        for task in self.browse(cr, SUPER_USER, ids, context=context):
            if task.sale_line_id:
                for f in field_names:
                    if f == 'sale_requested_date':
                        res[task.id][f] = task.sale_line_id.order_id.requested_date  
                    if f == 'sale_commitment_date':
                        res[task.id][f] = task.sale_line_id.order_id.commitment_date  
            
        return res
    
    _columns = {
        'origin': fields.char('Source Document', size=64),
        'date_start': fields.date('Start Date', select=True),
        'date_end': fields.date('End Date', select=True),
        'partner_address_id': fields.many2one('res.partner.address', 'Address'),
        'partner_address_city_id': fields.related('partner_address_id', 'city_id', type='many2one', relation='city.city', string='City'),
        'sale_requested_date': fields.function(_get_sale_dates, type='date', string='Requested date', multi='sale_dates', store=False),
        'sale_commitment_date': fields.function(_get_sale_dates, type='date', string='Commitment date', multi='sale_dates', store=False),
    }

task()

