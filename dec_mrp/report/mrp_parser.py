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

import time
from report import report_sxw
from tools.translate import _

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'manufacturer': self.get_manufacturer,
        })
        self.context = context

    def get_manufacturer(self, product):
        res = ''
        categ_id = product.categ_id
        if categ_id:
            while categ_id.parent_id and (categ_id.parent_id.id <> 1):
                categ_id = categ_id.parent_id

            if categ_id <> product.categ_id:
                res = ('%s - %s') % (categ_id.name, product.categ_id.name)
            else:
                res = ('%s') % (categ_id.name) 

        return res
        