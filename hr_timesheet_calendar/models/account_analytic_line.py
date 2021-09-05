# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    same_task_name = fields.Boolean(
        compute='_compute_same_task_name',
        help='Technical field to apply a filter when the task name equals '
        'the analytic one',
    )
    calendar_name = fields.Char(
        compute='_compute_same_task_name',
        help='Technical field to hide the name from calendar view since '
        'there is not support for invisible attrs in this kind of view',
    )

    @api.depends('name', 'task_id.name')
    def _compute_same_task_name(self):
        for rec in self:
            rec.calendar_name = rec.name
            if rec.task_id:
                rec.same_task_name = (rec.name == rec.task_id.name)
                if rec.same_task_name:
                    rec.calendar_name = ''
