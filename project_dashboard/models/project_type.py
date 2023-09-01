# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

import logging
from datetime import datetime

from odoo import _, api, fields, models
from odoo.addons.tools_miscellaneous.tools.context import (
    safe_eval_action_context_string_to_dict,
    safe_eval_active_context_dict_to_string,
)
from odoo.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)


class ProjectType(models.Model):
    _inherit = "project.type"

    dashboard_ok = fields.Boolean(
        string="Show in Dashboard",
        default=False,
    )
    open_default_groupby = fields.Char(
        string="Default Group By",
        help="Name of the field to use as default group by when "
        "opening projects of this type",
    )
    date_field = fields.Char(
        string="Date Reference",
        help="Name of the field to use as reference when computing "
        "projects count per year",
    )
    color = fields.Integer(
        string="Color Index",
        default=0,
    )
    project_ids = fields.One2many(
        comodel_name="project.project",
        inverse_name="type_id",
        string="Projects",
    )
    todo_project_count = fields.Integer(
        string="Number of projects",
        compute="_compute_todo_projects",
    )
    todo_project_count_unassigned = fields.Integer(
        string="Number of projects unassigned", compute="_compute_todo_projects"
    )
    todo_project_count_year_nm0 = fields.Integer(
        string="Number of projects from current year",
        compute="_compute_todo_projects",
    )
    todo_project_count_year_nm1 = fields.Integer(
        string="Number of projects from year-1",
        compute="_compute_todo_projects",
    )
    todo_project_count_year_nm2 = fields.Integer(
        string="Number of projects from year-2 and older",
        compute="_compute_todo_projects",
    )
    dashboard_project_ids = fields.One2many(
        comodel_name="project.project",
        inverse_name="type_id",
        string="Projects",
        domain=lambda self: [
            "|",
            "&",
            ("todo_task_count", ">", 0),
            "|",
            ("favorite_user_ids", "=", self.env.uid),
            ("message_is_follower", "=", True),
            ("dashboard_sequence", ">", 0),
        ],
        # We put the field context in the model definition because odoo 12
        # does not evaluate the field context in kanban view definition
        context={
            "kanban_fields": [
                "name",
                "display_name",
                "dashboard_sequence",
                "kanban_description",
            ]
        },
    )

    @api.depends(
        "project_ids",
        "project_ids.todo_task_count",
        "project_ids.todo_production_count",
    )
    def _compute_todo_projects(self):
        self.todo_project_count = 0
        self.todo_project_count_unassigned = 0
        self.todo_project_count_year_nm0 = 0
        self.todo_project_count_year_nm1 = 0
        self.todo_project_count_year_nm2 = 0
        Project = self.env["project.project"]
        type_ids = self.filtered("date_field")
        dashboard_dates = []
        for date in type_ids.mapped("date_field"):
            if date not in dashboard_dates:
                # Ensure that the named field exists in the model
                if date in Project._fields:
                    dashboard_dates.append(date)
                else:
                    _logger.warning(
                        _("Field %s not found in %s model") % (date, Project)
                    )
        result_per_date_reference = {}
        for date_field in dashboard_dates:
            date_field_year = date_field + ":year"
            child_ids = self.env["project.type"].search([("id", "child_of", self.ids)])
            fields = ["type_id", "user_id", date_field]
            groupby = ["type_id", "user_id", date_field_year]
            fetch_data = Project.read_group(
                [
                    ("type_id", "child_of", self.ids),
                    ("|"),
                    ("todo_task_count", ">", 0),
                    ("todo_production_count", ">", 0),
                ],
                fields=fields,
                groupby=groupby,
                lazy=False,
            )
            result_per_date_reference[date_field] = [
                [
                    data["type_id"][0],
                    data["user_id"] and data["user_id"][0],
                    data["__count"],
                    int(data[date_field_year]),
                ]
                for data in fetch_data
            ]

        COL_TYPE = 0
        COL_USER = 1
        COL_COUNT = 2
        COL_DATE = 3

        current_year = datetime.today().year
        for rec in type_ids:
            if rec.date_field not in dashboard_dates:
                # Ignore missing date field
                continue
            result = result_per_date_reference[rec.date_field]
            child_ids = self.env["project.type"].search([("id", "child_of", rec.id)])
            rec.todo_project_count = sum(
                [r[COL_COUNT] for r in result if r[COL_TYPE] in child_ids.ids]
            )
            rec.todo_project_count_unassigned = sum(
                [
                    r[COL_COUNT]
                    for r in result
                    if r[COL_TYPE] in child_ids.ids and not r[COL_USER]
                ]
            )
            rec.todo_project_count_year_nm0 = sum(
                [
                    r[COL_COUNT]
                    for r in result
                    if r[COL_TYPE] in child_ids.ids and r[COL_DATE] == current_year
                ]
            )
            rec.todo_project_count_year_nm1 = sum(
                [
                    r[COL_COUNT]
                    for r in result
                    if r[COL_TYPE] in child_ids.ids and r[COL_DATE] == current_year - 1
                ]
            )
            rec.todo_project_count_year_nm2 = sum(
                [
                    r[COL_COUNT]
                    for r in result
                    if r[COL_TYPE] in child_ids.ids
                    and r[COL_DATE]
                    and r[COL_DATE] <= current_year - 2
                ]
            )

    def action_open_project_from_dashboard(self):
        action = self.env.ref(
            "project_dashboard.action_project_kanban_from_dashboard"
        ).read()[0]
        context = safe_eval_action_context_string_to_dict(action)
        if len(self.ids) == 1:
            if self.date_field:
                context.update(
                    {
                        "date_field": self.date_field,
                    }
                )
            if self.open_default_groupby:
                context.update(
                    {
                        "group_by": self.open_default_groupby,
                    }
                )
            ctx_as_string = safe_eval_active_context_dict_to_string(context)
            return dict(action, context=ctx_as_string)
        else:
            return action

    def action_open_project(self):
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form,tree",
            "res_model": "project.project",
            "target": "current",
            "context": self.env.context,
            "res_id": self.env.context.get("project_id"),
        }

    def action_open_project_tasks(self):
        active_id = self.env.context.get("project_id")
        act = self.env.ref("project.act_project_project_2_project_task_all")
        action = act.read()[0]
        # Set active_id and active_ids to allow safe evaluation
        eval_ctx = dict(self.env.context)
        eval_ctx.update(
            {
                "active_id": active_id,
                "active_ids": [active_id],
            }
        )
        try:
            ctx = safe_eval(action.get("context", "{}"), eval_ctx)
        except:
            ctx = {}
        # Add or override `active_id` and `active_ids` otherwise the web
        # client keeps the `id` from the `project.type`
        ctx.update(
            {
                "active_id": active_id,
                "active_ids": [active_id],
            }
        )
        return dict(action, context=ctx)
