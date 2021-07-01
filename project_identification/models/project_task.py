# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import models, api, fields

SEARCH_SEPARATOR = ' →'


class ProjectTask(models.Model):
    _inherit = "project.task"

    project_type_id = fields.Many2one(
        comodel_name='project.type',
        string='Project Type',
        related='project_id.type_id',
        store=True,
    )

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if SEARCH_SEPARATOR in name:
            name = name.partition(SEARCH_SEPARATOR)[0]
            # Remove 'stage' emoji
            if name and not name[0].isalpha():
                name = name[1:].strip()
        names = super(ProjectTask, self.with_context(
            name_search=True
        )).name_search(name=name, args=args, operator=operator, limit=limit)
        return names

    @api.multi
    def name_get(self):
        if self.env.context.get('name_search'):
            return self.name_get_from_search()
        else:
            return super().name_get()

    @api.multi
    @api.depends('name', 'stage_id')
    def name_get_from_search(self):
        """ Custom naming with multiple identification parts to quickly
            identify a task
        """
        res = []
        for rec in self:
            name = rec.name
            identifications = rec._get_name_identifications()
            if identifications:
                name = '%s%s %s' % (
                    name, SEARCH_SEPARATOR, ' '.join(identifications)
                )
            if rec.stage_id and not rec.stage_id.name[0].isalpha():
                emoji = rec.stage_id.name[0]
                name = '%s %s' % (emoji, name)
            res.append((rec.id, name))
        return res

    @api.multi
    def _get_name_identifications(self):
        res = []
        self.ensure_one()
        # Add project to quickly identify a task
        project_id = self.project_id
        if project_id:
            project_name = project_id.name
            if project_id.type_id and not project_id.type_id.display_name[
                0].isalpha():
                emoji = project_id.type_id.display_name[0]
                project_name = '%s %s' % (emoji, project_name)
                res.append(project_name)
        return res
