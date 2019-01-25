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
import logging

log = logging.getLogger('dec.project')

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
        try:
            for task in self.browse(cr, SUPER_USER, ids, context=context):
                if task.sale_line_id and task.sale_line_id.order_id:
                    for f in field_names:
                        if f == 'sale_requested_date':
                            res[task.id][f] = task.sale_line_id.order_id.requested_date  
                        if f == 'sale_commitment_date':
                            res[task.id][f] = task.sale_line_id.order_id.commitment_date  
                        if f == 'sale_picked_rate':
                            res[task.id][f] = task.sale_line_id.order_id.picked_rate  
        except:
            pass
            
        return res
    
    def _get_view_name(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
             
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = ''
            if task.project_id:
                res[task.id] = '%s: ' % (task.project_id.name[:3].upper())  
                
            res[task.id] += '%s' % (task.name)  
            
            if task.partner_address_id and task.partner_address_id.city:
                res[task.id] += ' (%s)' % (task.partner_address_id.city)
            
        return res  

    def _get_analytic_account_ids(self, cr, uid, project_id=False, context=None):
        ids = []
        if project_id:
            project = self.pool.get('project.project').browse(cr, uid, project_id, context)
        else:
            user = self.pool.get('res.users') 
            project = user.browse(cr, uid, uid, context).context_project_id
            
        if project and project.analytic_account_id:
            ids.append(project.analytic_account_id.id)
            for analytic_account in project.child_complete_ids:
                ids.append(analytic_account.id)

        return ids

    def _get_project_ids(self, cr, uid, analytic_account_ids, context=None):
        ids = []
        project = self.pool.get('project.project') 
        args = ([('analytic_account_id', 'in', analytic_account_ids)])
        ids = project.search(cr, uid, args, context=context)
        return ids
    
    _columns = {
        'view_name': fields.function(_get_view_name, string='View name', type='char'), 
        'origin': fields.char('Source Document', size=64),
        'create_date' : fields.datetime('Create Date', readonly=True),
        'date_start': fields.date('Start Date', select=True),
        'date_end': fields.date('End Date', select=True),
        'partner_address_id': fields.many2one('res.partner.address', 'Address'),
        'partner_address_city_id': fields.related('partner_address_id', 'city_id', type='many2one', relation='city.city', string='City', store=True),
        'sale_requested_date': fields.function(_get_sale_dates, type='date', string='Requested date', multi='sale_dates', store=False),
        'sale_commitment_date': fields.function(_get_sale_dates, type='date', string='Commitment date', multi='sale_dates', store=False),
        'sale_picked_rate': fields.function(_get_sale_dates, type='float', string='Picked rate', multi='sale_dates', store=False),
        'meeting_id': fields.many2one('crm.meeting', 'Meeting'),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        if any(k in vals for k in ('name', 'date_start', 'date_end', 'user_id', 'partner_address_id')):
            meeting_obj = self.pool.get('crm.meeting')
            address_obj = self.pool.get('res.partner.address')
            for item in self.browse(cr, uid, ids, context):
                location = False
                address_id = vals.get('partner_address_id', False)
                if not address_id and item.partner_address_id and not 'partner_address_id' in vals:
                    location = item.partner_address_id.name_get()[0][1]
                if address_id and not location:
                    location = address_obj.browse(cr, uid, address_id, context).name_get()[0][1]
                data = {
                    'name': '🔒' + vals.get('name', item.name.encode('utf-8')),
                    'date': vals.get('date_start', item.date_start),
                    'date_deadline': vals.get('date_end', item.date_end),
                    'allday': True,
                    'user_id': vals.get('user_id', item.user_id.id),
                    'location': location, #item.partner_address_id and item.partner_address_id.name_get()[0][1] or False,
                    'description': "Ce rendez-vous a été créé automatiquement,"\
                        "pour le modifier vous devez modifier la tâche correspondante"
                }
                if not item.meeting_id:
                    meeting_id = meeting_obj.create(cr, uid, data, context=context)
                    self.write(cr, uid, ids, {'meeting_id' : meeting_id}, context)
                else:
                    meeting_obj.write(cr, uid, [item.meeting_id.id], data, context=context)


        return super(task, self).write(cr, uid, ids, vals, context)
    
    def create(self, cr, uid, vals, context=None):  
                
        # Hook to get back partner from production 
        production_obj = self.pool.get('mrp.production')           
        if vals.has_key('origin') and (vals.has_key('partner_id') and not vals['partner_id']) and (vals.has_key('partner_address_id') and not vals['partner_address_id']):
            for origin in vals['origin'].split(' '):
                for item in origin.split(':'):
                    if item.count('MO/') > 0:
                        production_ids = production_obj.search(cr, uid, [('name', '=', item)], context=context)
                        if len(production_ids) > 0:
                            production = production_obj.browse(cr, uid, production_ids, context)[0]
                            vals['partner_id'] = production.partner_id and production.partner_id.id or False
                            vals['partner_address_id'] = production.partner_address_id and production.partner_address_id.id or False                             
                            break
                    
        return super(task, self).create(cr, uid, vals, context)

    def _replace_project_id_with_childs_ids(self, cr, uid, args, context=None):
        if context is None:
            context = {}

        context_project_id = context.get('search_default_project_id', False)
        if context_project_id:
            del context['search_default_project_id']

        new_args = []
        replace_args = False
        for item in args:
            if isinstance(item, (list, tuple)) and len(item) == 3 and item[0] == 'project_id' and item[1] == '=':
                project_id = item[2]
                analytic_account_ids = self._get_analytic_account_ids(cr, uid, project_id, context)
                project_ids = self._get_project_ids(cr, uid, analytic_account_ids, context)
                new_item = ['project_id', 'in', project_ids]
                new_args.append(new_item)
                replace_args = True
                log.info(" Replacing item {0} with {1}".format(item, new_item))
            else:
                new_args.append(item)
                
        if replace_args:
            log.info("Replacing args \n {0} with \n {1}".format(args, new_args))
            args = new_args

        return args


    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        replace = context.get('replace_single_project_id', False)
        if replace:
            args = self._replace_project_id_with_childs_ids(cr, uid, args, context=context)
        res = super(task, self).search(cr, uid, args, offset, limit, order, context=context, count=count)
        return res


    def read_group(self, cr, uid, domain, fields, groupby, offset=0,
                   limit=None, context=None, orderby=False):
        
        domain = self._replace_project_id_with_childs_ids(cr, uid, domain, context=context)
        res = super(task, self).read_group(
            cr, uid, domain, fields, groupby,
            offset, limit, context, orderby)
        return res

task()

class project(osv.osv):
    _name = "project.project"
    _inherit = _name

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, uid, ['|', ('name', 'ilike', name),  ('parent_id', 'ilike', name)]+ args, limit=limit)

        return self.name_get(cr, uid, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for project in self.browse(cr, uid, ids, context=context):
            res.append((project.id, project.analytic_account_id.complete_name))
        return res


    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        res = super(project, self).search(cr, user, args, offset=offset, limit=limit, order=order,
            context=context, count=count)
        return res

    def read_group(self, cr, uid, domain, fields, groupby, offset=0,
                   limit=None, context=None, orderby=False):
        res = super(project, self).read_group(
            cr, uid, domain, fields, groupby,
            offset, limit, context, orderby)
        return res


project()

