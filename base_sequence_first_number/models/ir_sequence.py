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
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Jul 2020

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
