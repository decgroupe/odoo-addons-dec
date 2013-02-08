#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import wizard
import pooler

class city(osv.osv):

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for line in self.browse(cr, uid, ids, context=context):
            name = line.name
            if line.zip:
                name = "%s %s" % (line.zip, name)
            if line.state_id:
                name = "%s, %s" % (name, line.state_id.name)
            if line.country_id:
                name = "%s, %s" % (name, line.country_id.name)
            res.append((line['id'], name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, uid, [('zip', 'ilike', name)]+ args, limit=limit)
        if not ids:
            ids = self.search(cr, uid, [('name', operator, name)]+ args, limit=limit)
        return self.name_get(cr, uid, ids, context=context)

    _name = 'city.city'
    _description = 'City'
    _columns = {
        'state_id': fields.many2one('res.country.state', 'State',
            domain="[('country_id','=',country_id)]", select=1),
        'name': fields.char('City', size=64, required=True, select=1),
        'zip': fields.char('ZIP', size=64, required=True, select=1),
        'country_id': fields.many2one('res.country', 'Country', select=1),
        'code': fields.char('City Code', size=64,
            help="The official code for the city"),
    }
city()


class CountryState(osv.osv):
    _inherit = 'res.country.state'
    _columns = {
        'city_ids': fields.one2many('city.city', 'state_id', 'Cities'),
    }
CountryState()


class res_partner_address(osv.osv):
    _inherit = "res.partner.address"
    _columns = {
        'city_id': fields.many2one('city.city', 'Location', select=1),
        'zip': fields.related('city_id', 'zip', type="char", string="Zip",
                               store={}),
        'city': fields.related('city_id', 'name', type="char", string="City",
                               store={}),
        'state_id': fields.related('city_id', 'state_id', type="many2one",
                                   relation="res.country.state", string="State",
                                   store={}),
        'country_id': fields.related('city_id', 'country_id', type="many2one",
                                     relation="res.country", string="Country",
                                     store={}),
    }
res_partner_address()
