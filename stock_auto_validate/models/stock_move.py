# -*- coding: utf-8 -*-
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

from datetime import datetime
from dateutil import relativedelta
from itertools import groupby
from operator import itemgetter

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    auto_validate = fields.Boolean(
        'Auto Validate',
        old_name="openupgrade_legacy_8_0_auto_validate",
        help="Also validate linked moves when this move is validated.",
        copy=False,
    )

    def _action_done(self):
        res = super()._action_done()
        auto_validated_moves = res.\
            mapped('move_dest_ids').\
            filtered(lambda m: m.auto_validate and m.state == 'assigned')
        for move in auto_validated_moves:
            # Apply logic from addons/stock/wizard/stock_immediate_transfer.py
            # and process every move lines
            for move_line in move.move_line_ids:
                move_line.qty_done = move_line.product_uom_qty
        # Finally call action_done
        if auto_validated_moves:
            auto_validated_moves._action_done()
        return res
