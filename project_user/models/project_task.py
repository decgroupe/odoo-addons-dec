# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024

from odoo import Command, api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def default_get(self, default_fields):
        rec = super().default_get(default_fields)
        if self.env.context.get("default_project_id"):
            project_id = self.env["project.project"].browse(
                self.env.context.get("default_project_id")
            )
            if project_id.exists() and project_id.default_task_user_ids:
                rec["user_ids"] = [Command.set(project_id.default_task_user_ids.ids)]
        return rec

    def action_assign_to_me(self):
        self.write({"user_ids": [Command.link(self.env.user.id)]})
