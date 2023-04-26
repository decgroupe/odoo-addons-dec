# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import _, api, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.model
    def action_view_base(self):
        view_kanban_id = self.env.ref("project.view_project_kanban")
        view_form_id = self.env.ref("project.edit_project")
        view_list_id = self.env.ref("project.view_project")
        action = {
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.ids)],
            "views": [
                (view_kanban_id.id, "kanban"),
                (view_list_id.id, "tree"),
                (view_form_id.id, "form"),
            ],
            "view_mode": "kanban,tree,form",
            "name": _("Projects"),
            "res_model": "project.project",
        }
        return action

    def action_view(self):
        action = self.action_view_base()
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            action["domain"] = [("id", "in", self.ids)]
        else:
            action["res_id"] = self.ids[0]
        return action

    def action_view_tasks(self):
        action = self.mapped("task_ids").action_view()
        action["context"] = {}
        return action
