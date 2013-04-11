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


class res_partner(osv.osv):
    _name = "res.partner"
    _inherit="res.partner"
    _columns = {
        'partner_academy': fields.many2one('res.partner.academy', 'Academy', help="Educational academy of the current partner."),
        'academy': fields.char('Academy', size=128, help="Educational academy of the current partner."),
        'zip': fields.related('address', 'zip', type='char', string='Zip'),
    }

res_partner()

class res_partner_academy(osv.osv):
    """ Description """

    _name = 'res.partner.academy'
    _description = 'Academy'
    _rec_name = 'name'

    _columns = {     
        'name': fields.text('Name', required=True),
    }

    _defaults = {

    }
 
    _order = 'name'

res_partner_academy()


