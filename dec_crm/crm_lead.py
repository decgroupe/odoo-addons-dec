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


class crm_lead(osv.osv):
    """ CRM Lead Case """
    _name = "crm.lead"
    _inherit = _name

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

crm_lead()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
