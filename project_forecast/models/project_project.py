# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

from odoo import api, fields, models


class Project(models.Model):
    _inherit = ['project.project', 'mail.activity.forecast.mixin']
    _name = 'project.project'

    def _get_forecast_date_fields(self):
        res = super()._get_forecast_date_fields()
        res.update(
            {
                'start': 'date_start',
                'stop': 'date',
                'deadline': 'date',
            }
        )
        return res

    @api.multi
    @api.depends("active")
    def _compute_schedulable(self):
        super()._compute_schedulable()

    @api.multi
    def _is_schedulable(self):
        res = super()._is_schedulable()
        if res:
            if not self.active:
                res = False
        return res
