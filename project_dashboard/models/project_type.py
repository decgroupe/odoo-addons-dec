# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

import json
import logging
from datetime import datetime

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

from odoo.addons.tools_miscellaneous.tools.context import (
    safe_eval_action_context_string_to_dict,
    safe_eval_active_context_dict_to_string,
)

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
        default="create_date",
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
    kanban_dashboard = fields.Text(
        compute="_compute_kanban_dashboard",
    )

    def _get_dashboard_data(self):
        dashboard_data = {}
        for rec in self:
            project_ids = self.env["project.project"].search(
                # domain explanation: we want to display in the dashboard all projects
                # per type that are either:
                # - having tasks to do and followed/favorited by the user
                # - or simply having a dashboard sequence defined (to force visibility
                #   on dashboard even without tasks or followers)
                [
                    ("type_id", "child_of", rec.id),
                    "|",
                    "&",
                    ("todo_task_count", ">", 0),
                    "|",
                    ("favorite_user_ids", "=", self.env.uid),
                    ("message_is_follower", "=", True),
                    ("dashboard_sequence", ">", 0),
                ],
                order="dashboard_sequence desc, sequence, name, id",
            )
            projects = []
            for project in project_ids:
                projects.append(
                    {
                        "id": project.id,
                        "name": project.name,
                        "display_name": project.display_name,
                        "dashboard_sequence": project.dashboard_sequence,
                        "kanban_description": project.kanban_description,
                    }
                )
            dashboard_data[rec.id] = {
                "projects": projects,
            }
        return dashboard_data

    @api.depends("project_ids", "project_ids.task_ids")
    def _compute_kanban_dashboard(self):
        dashboard_data = self._get_dashboard_data()
        for rec in self:
            rec.kanban_dashboard = json.dumps(dashboard_data[rec.id])

    @api.depends(
        "date_field",
        "project_ids",
        "project_ids.type_id",
        "project_ids.todo_task_count",
        "project_ids.todo_production_count",
    )
    def _compute_todo_projects(self):
        # zeroing all counts
        self.todo_project_count = 0
        self.todo_project_count_unassigned = 0
        self.todo_project_count_year_nm0 = 0
        self.todo_project_count_year_nm1 = 0
        self.todo_project_count_year_nm2 = 0
        current_year = datetime.today().year

        Project = self.env["project.project"]
        # keep only types with `date_field` set for the search and groupby to avoid
        # unnecessary load of all projects of types without `date_field`
        type_ids = self.filtered("date_field")
        # group by `type_id`, `user_id` and year of `type_date` (which is a copy of
        # the content of the date field defined on type)
        groupby = ["type_id", "user_id", "type_date:year"]
        aggregates = ["__count"]
        domain = [
            ("type_id", "child_of", self.ids),
            ("|"),
            ("todo_task_count", ">", 0),
            ("todo_production_count", ">", 0),
        ]
        fetch_data = Project._read_group(
            domain=domain,
            groupby=groupby,
            aggregates=aggregates,
        )
        # map fetch_data to a dict with keys `type_id`, `user_id` and `year`
        # for easier use in the loop below
        result = [
            {
                "type_id": type_id.id,
                "user_id": user_id.id,
                "year": type_date.year if type_date else current_year,
                "count": count,
            }
            for type_id, user_id, type_date, count in fetch_data
        ]
        # compute counts on project type based on the grouped data. We loop only on
        # types with `date_field` defined to avoid unnecessary loops

        for rec in type_ids:
            child_ids = self.env["project.type"].search([("id", "child_of", rec.id)])
            rec.todo_project_count = sum(
                [r["count"] for r in result if r["type_id"] in child_ids.ids]
            )
            rec.todo_project_count_unassigned = sum(
                [
                    r["count"]
                    for r in result
                    if r["type_id"] in child_ids.ids and not r["user_id"]
                ]
            )
            rec.todo_project_count_year_nm0 = sum(
                [
                    r["count"]
                    for r in result
                    if r["type_id"] in child_ids.ids and r["year"] == current_year
                ]
            )
            rec.todo_project_count_year_nm1 = sum(
                [
                    r["count"]
                    for r in result
                    if r["type_id"] in child_ids.ids and r["year"] == current_year - 1
                ]
            )
            rec.todo_project_count_year_nm2 = sum(
                [
                    r["count"]
                    for r in result
                    if r["type_id"] in child_ids.ids
                    and r["year"]
                    and r["year"] <= current_year - 2
                ]
            )

    def action_open_projects_from_dashboard(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "project_dashboard.action_project_kanban_from_dashboard"
        )
        context = safe_eval_action_context_string_to_dict(action)
        if len(self.ids) == 1:
            if self.open_default_groupby:
                context.update({"group_by": self.open_default_groupby})
            ctx_as_string = safe_eval_active_context_dict_to_string(context)
            return dict(action, context=ctx_as_string)
        else:
            return action

    def action_open_project(self):
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form,list",
            "res_model": "project.project",
            "target": "current",
            "context": self.env.context,
            "res_id": self.env.context.get("project_id"),
        }

    def action_open_project_tasks(self):
        active_id = self.env.context.get("project_id")
        action = self.env["ir.actions.actions"]._for_xml_id(
            "project.act_project_project_2_project_task_all"
        )
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
        except Exception as e:
            _logger.error("Error while evaluating action context: %s", e)
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

    def action_open_all_projects(self):
        # use action from `project_action_view`
        action = self.mapped("project_ids").action_view()
        return action

    def action_open_all_projects_tasks(self):
        # use action from `project_action_view`
        action = self.mapped("project_ids").action_view_all_tasks()
        return action
