# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = ['project.task', 'mail.activity.schedule.mixin']
    _name = 'project.task'

    def _get_schedule_date_fields(self):
        res = super()._get_schedule_date_fields()
        res.update(
            {
                'start': 'date_start',
                'stop': 'date_end',
                'deadline': 'date_deadline',
            }
        )
        return res
