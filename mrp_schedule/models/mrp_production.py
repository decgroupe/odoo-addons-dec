# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = ["mrp.production", "mail.activity.schedule.mixin"]
    _name = "mrp.production"

    def _get_schedule_date_fields(self):
        res = super()._get_schedule_date_fields()
        res.update(
            {
                "start": "date_planned_start",
                "stop": "date_planned_finished",
                "deadline": "date_planned_finished",
            }
        )
        return res

    @api.multi
    @api.depends("state")
    def _compute_schedulable(self):
        super()._compute_schedulable()

    @api.multi
    def _is_schedulable(self):
        res = super()._is_schedulable()
        if res and self.state in ["done", "cancel"]:
            res = False
        return res
