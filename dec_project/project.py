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

#
#
#class project_task_type(osv.osv):
#    _name = 'project.task.type'
#    _inherit =_name
#
#project_task_type()
#
#class project(osv.osv):
#    _name = "project.project"
#    _inherit = _name
#
#project()
#
#
#class task(osv.osv):
#    _name = "project.task"
#    _inherit = _name
#
#task()
#
#class project_work(osv.osv):
#    _name = "project.task.work"
#    _inherit = _name
#   
#project_work()
#
##
## Tasks History, used for cumulative flow charts (Lean/Agile)
##
#
#class project_task_history(osv.osv):
#    _name = 'project.task.history'
#    _inherit = _name
#    
#project_task_history()
#
#class project_task_history_cumulative(osv.osv):
#    _name = 'project.task.history.cumulative'
#    _inherit = _name
#    
#
#project_task_history_cumulative()

