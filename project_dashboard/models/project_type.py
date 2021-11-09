# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from datetime import datetime, timedelta

from odoo import _, api, fields, models


class ProjectType(models.Model):
    _inherit = 'project.type'

    dashboard_ok = fields.Boolean(
        string='Show in Dashboard',
        default=False,
    )
    color = fields.Integer(
        string="Color Index",
        default=0,
    )
    project_ids = fields.One2many(
        comodel_name='project.project',
        inverse_name='type_id',
        string="Projects",
    )
    todo_project_count = fields.Integer(
        string="Number of projects",
        compute='_compute_todo_projects',
    )
    todo_project_count_unassigned = fields.Integer(
        string="Number of projects unassigned",
        compute='_compute_todo_projects'
    )
    todo_project_count_year_nm0 = fields.Integer(
        string="Number of projects from current year",
        compute='_compute_todo_projects',
    )
    todo_project_count_year_nm1 = fields.Integer(
        string="Number of projects from year-1",
        compute='_compute_todo_projects',
    )
    todo_project_count_year_nm2 = fields.Integer(
        string="Number of projects from year-2 and older",
        compute='_compute_todo_projects',
    )

    @api.depends(
        'project_ids', 'project_ids.todo_task_count',
        'project_ids.todo_production_count'
    )
    def _compute_todo_projects(self):
        project_model = self.env["project.project"]
        child_ids = self.env["project.type"].search(
            [('id', 'child_of', self.ids)]
        )
        fields = ["type_id", "user_id", "contract_confirmation_date"]
        groupby = ["type_id", "user_id", "contract_confirmation_date:year"]
        fetch_data = project_model.read_group(
            [
                ("type_id", "child_of", self.ids),
                ('|'),
                ("todo_task_count", ">", 0),
                ("todo_production_count", ">", 0),
            ],
            fields=fields,
            groupby=groupby,
            lazy=False,
        )

        COL_TYPE = 0
        COL_USER = 1
        COL_COUNT = 2
        COL_DATE = 3
        result = [
            [
                data["type_id"][0],
                data["user_id"] and data["user_id"][0],
                data["__count"],
                int(data["contract_confirmation_date:year"]),
            ] for data in fetch_data
        ]
        current_year = datetime.today().year
        for rec in self:
            child_ids = self.env["project.type"].search(
                [('id', 'child_of', rec.id)]
            )
            rec.todo_project_count = sum(
                [r[COL_COUNT] for r in result if r[COL_TYPE] in child_ids.ids]
            )
            rec.todo_project_count_unassigned = sum(
                [
                    r[COL_COUNT] for r in result
                    if r[COL_TYPE] in child_ids.ids and not r[COL_USER]
                ]
            )
            rec.todo_project_count_year_nm0 = sum(
                [
                    r[COL_COUNT] for r in result if
                    r[COL_TYPE] in child_ids.ids and r[COL_DATE] == current_year
                ]
            )
            rec.todo_project_count_year_nm1 = sum(
                [
                    r[COL_COUNT]
                    for r in result if r[COL_TYPE] in child_ids.ids and
                    r[COL_DATE] == current_year - 1
                ]
            )
            rec.todo_project_count_year_nm2 = sum(
                [
                    r[COL_COUNT]
                    for r in result if r[COL_TYPE] in child_ids.ids and
                    r[COL_DATE] and r[COL_DATE] <= current_year - 2
                ]
            )
