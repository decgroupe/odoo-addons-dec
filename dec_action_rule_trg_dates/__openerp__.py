# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher (Camptocamp) 
#    Contributor: 
#    Copyright 2011 Camptocamp SA
#    Donors:
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
{
     "name" : "DEC action rule trigger dates",
     "version" : "1.0",
     "author" : "Camptocamp",
     "category" : "Generic Modules/Others",
     "description":
"""
This module makes all date of a model available as a triggering date in action rule

Change the static trigger date selection into a 
one2many on date and datetime fields of the model
""",
     "website": "http://camptocamp.com",
     "depends" : ['base','base_action_rule'],
     "init_xml" : [],
     "demo_xml" : [],
     "update_xml" : [
                    'action_rule_view.xml',
                     ],
     "active": False,
     "installable": True
}
