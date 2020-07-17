# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import api, fields, models, _


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    number_first = fields.Integer(
        string='First Number',
        default=1,
        help="First number of a date range of this sequence after create or reset"
    )

    def _create_date_range_seq(self, date):
        seq_date_range = super()._create_date_range_seq(date)
        seq_date_range.number_next = self.number_first or self.number_next_actual or 1
        return seq_date_range
