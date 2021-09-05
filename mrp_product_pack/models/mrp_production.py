# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def update_move_raw_sequences(self):
        for production in self:
            moves = production.move_raw_ids.sorted(key=lambda x: x.id)
            moves._update_sequence()
