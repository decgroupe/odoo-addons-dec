# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import models, api, fields


class ProjectTask(models.Model):
    _inherit = "project.task"

    project_type_id = fields.Many2one(
        comodel_name='project.type',
        string='Project Type',
        related='project_id.type_id',
    )

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # Make a search with default criteria
        names = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        # Add project to quickly identify a task
        result = []
        for item in names:
            task = self.browse(item[0])[0]
            name = item[1]
            project_id = task.project_id
            if project_id:
                project_name = project_id.name
                if project_id.type_id and not project_id.type_id.display_name[0].isalpha():
                    emoji = project_id.type_id.display_name[0]
                    project_name = '%s %s' % (emoji, project_name)
                name = '%s (%s)' % (name, project_name)
            if task.stage_id and not task.stage_id.name[0].isalpha():
                emoji = task.stage_id.name[0]
                name = '%s %s' % (emoji, name)
            result.append((item[0], name))
        return result
