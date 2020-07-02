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

    auto_validate = fields.Boolean('Auto Validate')

    def _action_done(self):
        moves_todo = super()._action_done()
        next_moves_todo = moves_todo.\
            mapped('move_dest_ids').\
            filtered(lambda m: m.auto_validate and m.state == 'assigned')
        if next_moves_todo:
            next_moves_todo._action_done()
        return moves_todo
