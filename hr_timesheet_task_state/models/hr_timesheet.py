# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import models, api, fields


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    task_stage_id = fields.Many2one(
        comodel_name="project.task.type",
        string="Task state",
        related="task_id.stage_id",
        readonly=False,
    )
