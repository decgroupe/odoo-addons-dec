# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from datetime import datetime, timedelta

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    _order = "date_time desc"

    date_time = fields.Datetime(
        default=lambda self: self._default_date_time(),
        copy=False,
    )

    @api.model
    def _default_date_time(self):
        """Round the current datetime to the previous quarter of an hour.
        - Exact boundary: 14:00:00 -> 14:00:00
        - Mid-period: 14:07:30 -> 14:00:00
        - Just before boundary: 14:14:59 -> 14:00:00
        - Exact boundary: 14:15:00 -> 14:15:00
        - Just after boundary: 14:16:00 -> 14:15:00
        - End of period: 14:29:59 -> 14:15:00
        """

        def ceil_dt(dt, delta):
            return dt + (datetime.min - dt) % delta

        return ceil_dt(fields.Datetime.now(), timedelta(minutes=-15))
