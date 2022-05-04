# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = ['mrp.production', 'mail.activity.forecast.mixin']
    _name = 'mrp.production'

    def _get_scheduling_activity_deadline(self):
        res = super()._get_scheduling_activity_deadline()
        # FIXME: This date should be taken from the picking or the initial
        # sale order
        res = self.date_planned_finished
        return res

    def _get_forecast_date_fields(self):
        return "date_planned_start", "date_planned_finished"
