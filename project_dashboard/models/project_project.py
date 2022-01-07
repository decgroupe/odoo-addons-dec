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
