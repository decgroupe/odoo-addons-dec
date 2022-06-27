# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2021

from datetime import datetime, timedelta

from odoo import _, api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'
    _order = "dashboard_sequence desc, sequence, name, id"

    dashboard_sequence = fields.Integer(
        string="Dashboard Position",
        default=0,
        help="If set, then this project will be displayed on the "
        "dashboard. A higher value indicats an higher priority."
    )

    kanban_description = fields.Char(compute="_compute_kanban_description")

    @api.multi
    def _compute_kanban_description(self):
        for rec in self:
            rec.kanban_description = rec.partner_shipping_id.display_name

    def action_open_all_tasks(self):
        act = self.with_context(
            active_id=False,
            active_ids=False,
            active_model=False,
        ).env.ref("project.act_project_project_2_project_task_all").read()[0]

        act['context'] = {}
        act['domain'] = [('project_id', 'in', self.ids)]
        return act
