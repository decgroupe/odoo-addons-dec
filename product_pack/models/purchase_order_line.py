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


class purchase_order_line(models.Model):

    _inherit = 'purchase.order.line'

    sequence = fields.integer(
        'Sequence',
        help=
        "Gives the sequence order when displaying a list of purchase order lines."
    )
    pack_depth = fields.integer(
        'Depth',
        default=lambda *a: 0,
        required=True,
        help='Depth of the product if it is part of a pack.'
    )
    pack_parent_line_id = fields.Many2one(
        'purchase.order.line',
        'Pack',
        help='The pack that contains this product.'
    )
    pack_child_line_ids = fields.One2many(
        'purchase.order.line', 'pack_parent_line_id', 'Lines in pack', help=''
    )
    pack_expand = fields.Boolean(
        'Pack expand',
        default=True,
        help=
        'If checked, the product pack will be automatically expanded when computed'
    )
    pack_print = fields.Boolean(
        'Pack print',
        default=True,
        help='If checked, the product pack content will be print'
    )

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}

        default.update({'pack_child_line_ids': False, 'pack_depth': 0})
        result = super(purchase_order_line,
                       self).copy_data(cr, uid, id, default, context=context)
        if result.get('pack_parent_line_id', False) <> False:
            result['pack_delete'] = True

        return result
