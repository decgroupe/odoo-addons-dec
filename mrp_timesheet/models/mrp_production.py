# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    allow_timesheets = fields.Boolean(
        "Allow timesheets",
        default=True,
    )
    planned_hours = fields.Float(
        string='Planned Hours',
        track_visibility='onchange',
    )
    progress = fields.Float(
        compute='_compute_progress_hours',
        group_operator='avg',
        store=True,
        string='Progress',
    )
    remaining_hours = fields.Float(
        compute='_compute_progress_hours',
        readonly=True,
        store=True,
        string='Remaining Hours',
    )
    timesheet_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='production_id',
        string='Timesheet',
    )
    total_hours = fields.Float(
        compute='_compute_total_hours',
        readonly=True,
        store=True,
        string='Total Hours'
    )

    @api.depends('timesheet_ids.unit_amount')
    def _compute_total_hours(self):
        for record in self:
            record.total_hours = sum(
                record.timesheet_ids.mapped('unit_amount')
            )

    @api.constrains('project_id')
    def _constrains_project_timesheets(self):
        if not self.env.context.get('ignore_constrains_project_timesheets'):
            for record in self:
                record.timesheet_ids.update({
                    'project_id': record.project_id.id
                })

    @api.depends('planned_hours', 'total_hours')
    def _compute_progress_hours(self):
        for record in self:
            record.progress = 0.0
            if (record.planned_hours > 0.0):
                if record.total_hours > record.planned_hours:
                    record.progress = 100
                else:
                    record.progress = round(
                        100.0 * record.total_hours / record.planned_hours,
                        2
                    )
            record.remaining_hours = record.planned_hours - record.total_hours
