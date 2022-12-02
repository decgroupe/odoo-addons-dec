# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    posted_in_timesheet = fields.Boolean(
        string='Posted in Timesheets',
        compute="_compute_posted_in_timesheet",
        store=True,
    )

    @api.depends(
        'task_id', 'task_id.exclude_from_timesheet', 'project_id',
        'project_id.exclude_from_timesheet'
    )
    def _compute_posted_in_timesheet(self):
        for rec in self:
            rec.posted_in_timesheet = True
            if rec.project_id:
                if rec.project_id.exclude_from_timesheet:
                    rec.posted_in_timesheet = False
            if rec.task_id:
                if rec.task_id.exclude_from_timesheet:
                    rec.posted_in_timesheet = False
