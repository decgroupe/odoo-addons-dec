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

import datetime
import time

import tools
from osv import fields, osv
from tools.translate import _

class account_followup_print_all(osv.osv_memory):
    _name = 'account.followup.print.all'
    _inherit = _name

    def do_print(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        res = super(account_followup_print_all, self).do_print(cr, uid, ids, context=context)
        res['report_name'] = 'service_print_account_followup'
        return res

account_followup_print_all()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
