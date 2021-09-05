# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

from odoo import api, models, fields


class Project(models.Model):
    _inherit = "project.project"

    todo_task_count = fields.Integer(
        string="To-Do Task Count",
        compute='_compute_todo_task_count',
        store=True,
        help="Number of currently open tasks",
    )

    @api.multi
    @api.depends('task_ids', 'task_ids.stage_id', 'task_ids.type_id')
    def _compute_todo_task_count(self):
        time_tracking_type = self.env.ref(
            'project_identification.time_tracking_type'
        )
        task_data = self.env['project.task'].read_group(
            [
                ('project_id', 'in', self.ids),
                '|',
                ('stage_id.fold', '=', False),
                ('stage_id', '=', False),
                '|',
                ('type_id', '=', False),
                ('type_id', '!=', time_tracking_type.id),
            ], ['project_id'], ['project_id']
        )
        result = dict(
            (data['project_id'][0], data['project_id_count'])
            for data in task_data
        )
        for rec in self:
            rec.todo_task_count = result.get(rec.id, 0)
