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
from datetime import datetime
from tools.translate import _


class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = _name
    
    _columns = {
        'crm_lead_ids': fields.many2many('crm.lead', 'sale_order_crm_lead_ids', 'sale_order_id', 'crm_lead_id', 'CRM leads', domain=[]),  
    }
    
sale_order()

class crm_lead(osv.osv):
    """ CRM Lead Case """
    _name = "crm.lead"
    _inherit = _name
    
    _columns = {
        'sale_order_ids': fields.many2many('sale.order', 'sale_order_crm_lead_ids', 'crm_lead_id', 'sale_order_id', 'Sale orders', domain=[]),  
    }

    def unsubscribe(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
          ids = [ids]
          
        assert len(ids) == 1, 'Unsubscribe may only be done one at a time'
        
        lead = self.browse(cr, uid, ids[0], context=context)
        url = ''
        def extract(raw_string, start_marker, end_marker):
            start = raw_string.index(start_marker) + len(start_marker)
            try:
                end = raw_string.index(end_marker, start)
            except:
                end = None
            return raw_string[start:end]
        
        for line in lead.description.split('\n'):
            if 'http://' in line:
                url = extract(line,'http://', ' ')
          
        if url: 
            return {
            'type': 'ir.actions.act_url',
            'url': 'http://' + url,
            'target': 'new'
            }
        else:
            return False
        
    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
          ids = [ids]
          
        if not vals:
            vals= {}
            
        if 'ref' in vals and vals['ref']:
            values = vals['ref'].split(',')
            if values and values[1].isdigit():
                model_name = values[0] 
                model_id = int(values[1])  
                if model_name == 'sale.order' and model_id > 0:
                    vals.update({
                        'sale_order_ids': [(4, model_id)],
                        })
            
        result = super(crm_lead,self).write(cr, uid, ids, vals, context)
        return result

crm_lead()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
