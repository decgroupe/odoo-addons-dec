# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    todo_task_count = fields.Integer(
        string="To-Do Task Count",
        compute="_compute_todo_task_count",
        store=True,
        help="Number of currently open tasks",
    )

    @api.depends("task_ids", "task_ids.is_closed", "task_ids.type_id")
    def _compute_todo_task_count(self):
        self.todo_task_count = 0
        time_tracking_type = self.env.ref("project_identification.time_tracking_type")
        domain = [
            ("project_id", "in", self.ids),
            ("is_closed", "=", False),
            # exclude time-tracking tasks from the count
            ("type_id", "!=", time_tracking_type.id),
        ]
        task_data = self.env["project.task"]._read_group(
            domain,
            ["project_id"],
            ["__count"],
        )
        for project, count in task_data:
            project.todo_task_count = count
