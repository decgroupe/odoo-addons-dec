# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = ['mrp.production', 'mail.activity.forecast.mixin']
    _name = 'mrp.production'

    def _get_forecast_date_fields(self):
        res = super()._get_forecast_date_fields()
        res.update(
            {
                'start': 'date_planned_start',
                'stop': 'date_planned_finished',
                'deadline': 'date_planned_finished',
            }
        )
        return res