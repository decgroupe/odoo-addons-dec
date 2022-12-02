# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def action_view_base(self):
        return self.env.ref('project.action_view_task').read()[0]

    def action_view(self):
        action = self.action_view_base()
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            action['domain'] = [('id', 'in', self.ids)]
        else:
            form = self.env.ref('project.view_task_form2')
            action['views'] = [(form.id, 'form')]
            action['res_id'] = self.ids[0]
        return action

    @api.model
    def action_view_project_base(self):
        return self.env.ref('project.open_view_project_all').read()[0]

    def action_view_project_form(self):
        self.ensure_one()
        action = self.action_view_project_base()
        action['res_id'] = self.project_id.id
        action['view_mode'] = 'form'
        view = self.env.ref("project.edit_project", False)
        action["views"] = [(view and view.id or False, "form")]
        action['context'] = {}
        # Replace main with current to avoid clearing breadcrumb
        action['target'] = 'current'
        return action
