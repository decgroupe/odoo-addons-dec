# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import fields, models

from odoo.addons.project.models.project_task import CLOSED_STATES


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    task_id = fields.Many2one(
        # override static domain set by OCA module `hr_timesheet_task_domain`
        domain="task_id_domain",
    )
    task_id_domain = fields.Binary(
        string="Task Domain",
        help="Dynamic domain used for the `task_id` field",
        compute="_compute_task_id_domain",
    )

    def _compute_task_id_domain(self):
        """Compute dynamic domain for the task_id field."""
        for rec in self:
            domain = [
                ("company_id", "in", (rec.company_id.id, False)),
                ("project_id.allow_timesheets", "=", True),
            ]
            if rec.project_id:
                if self.env.context.get("keep_hr_timesheet_task_domain", False):
                    # default domain defined by OCA module `hr_timesheet_task_domain`
                    # is kept if the context key `keep_hr_timesheet_task_domain` is True
                    domain += [
                        ("state", "not in", list(CLOSED_STATES.keys())),
                        ("project_id", "=", rec.project_id.id),
                    ]
                else:
                    # otherwise, only filter tasks of the selected project without
                    # excluding closed tasks
                    domain += [
                        ("project_id", "=?", rec.project_id.id),
                    ]
            rec.task_id_domain = domain
