# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Mar 2020

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class sale_order_line(models.Model):

    _inherit = 'sale.order.line'

    pack_depth = fields.integer(
        'Depth',
        required=True,
        default=lambda *a: 0,
        help='Depth of the product if it is part of a pack.'
    )
    pack_parent_line_id = fields.Many2one(
        'sale.order.line', 'Pack', help='The pack that contains this product.'
    )
    pack_child_line_ids = fields.One2many(
        'sale.order.line', 'pack_parent_line_id', 'Lines in pack', help=''
    )
    pack_expand = fields.Boolean(
        'Pack expand',
        default=True,
        help=
        'If checked, the product pack will be automatically expanded when computed'
    )


    def create(self, cr, user, vals, context=None):
        result = False
        result = super(sale_order_line, self).create(cr, user, vals, context)
        return result

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}

        default.update({'pack_child_line_ids': False, 'pack_depth': 0})
        result = super(sale_order_line,
                       self).copy_data(cr, uid, id, default, context=context)
        if result.get('pack_parent_line_id', False) <> False:
            result['pack_delete'] = True

        return result
