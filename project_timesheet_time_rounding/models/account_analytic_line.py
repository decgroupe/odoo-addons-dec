# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from datetime import datetime, timedelta

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    _order = "date_time desc"

    @api.model
    def _default_date_time(self):
        def ceil_dt(dt, delta):
            return dt + (datetime.min - dt) % delta

        return ceil_dt(fields.Datetime.now(), timedelta(minutes=-15))

    date_time = fields.Datetime(
        default=_default_date_time,
        copy=False,
    )
