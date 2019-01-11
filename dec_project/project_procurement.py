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

from osv import fields, osv
from tools.translate import _

class procurement_order(osv.osv):
    _name = "procurement.order"
    _inherit = "procurement.order"

    def action_produce_assign_service(self, cr, uid, ids, context=None):
        project_task = self.pool.get('project.task')
        
        if context is None:
            context = {}
            
        context['lang'] = self.pool.get('res.users').browse(cr, uid, uid, context=context).context_lang
        
        for procurement in self.browse(cr, uid, ids, context=context):
            project = self._get_project(cr, uid, procurement, context=context)
            planned_hours = self._convert_qty_company_hours(cr, uid, procurement, context=context)
            task_id = project_task.create(cr, uid, {
                'name': '[%s] %s: %s: %s %s' % (procurement.product_id.default_code, procurement.product_id.name, procurement.name, procurement.product_qty, procurement.product_uom.name),
                'origin': procurement.origin,
                'date_deadline': procurement.date_planned,
                'planned_hours':planned_hours,
                'remaining_hours': planned_hours,
                'user_id': procurement.product_id.product_manager.id,
                #'notes': procurement.note,
                'procurement_id': procurement.id,
                'description': procurement.note,
                'project_id':  project and project.id or False,
                'company_id': procurement.company_id.id,
                'partner_id': procurement.sale_line_id.order_id and procurement.sale_line_id.order_id.partner_shipping_id.partner_id.id or False,
                'partner_address_id': procurement.sale_line_id.order_id and procurement.sale_line_id.order_id.partner_shipping_id.id or False,
            },context=context)
            self.write(cr, uid, [procurement.id], {'task_id': task_id, 'state': 'running', 'message':_('from project: task created.')}, context=context)
        return task_id

procurement_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
