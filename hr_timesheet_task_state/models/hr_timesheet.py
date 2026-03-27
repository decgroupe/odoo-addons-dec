# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    """Add task stage field to timesheet lines."""

    _inherit = "account.analytic.line"

    task_stage_id = fields.Many2one(
        comodel_name="project.task.type",
        string="Task state",
        related="task_id.stage_id",
        readonly=False,
    )
