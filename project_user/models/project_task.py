# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def default_get(self, default_fields):
        rec = super().default_get(default_fields)
        if self.env.context.get("default_project_id"):
            project_id = self.env["project.project"].browse(
                self.env.context.get("default_project_id")
            )
            if project_id.exists() and project_id.default_task_user_id:
                rec["user_id"] = project_id.default_task_user_id.id
        return rec
