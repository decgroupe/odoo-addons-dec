# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

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

    @api.model
    def create(self, values):
        if not values.get('allow_timesheets') is True:
            self_ctx = self.with_context(mrp_project_auto_disable=True)
        else:
            self_ctx = self
        production_id = super(MrpProduction, self_ctx).create(values)
        # Do not call `action_create_project` here since it will be probably
        # too late, instead, we override `_generate_moves` to call it befrore
        # generating any moves
        return production_id

    def write(self, vals):
        res = super().write(vals)
        if 'planned_hours' in vals:
            self.onchange_planned_hours()
        return res

    @api.depends('timesheet_ids.unit_amount')
    def _compute_total_hours(self):
        for rec in self:
            rec.total_hours = sum(rec.timesheet_ids.mapped('unit_amount'))
            # Automatically set state to "In Progress" if a timesheet input
            # is added to this production order
            if rec.total_hours > 0 and rec._allow_auto_start():
                rec.action_start()

    @api.constrains('project_id')
    def _constrains_project_timesheets(self):
        if not self.env.context.get('ignore_constrains_project_timesheets'):
            for rec in self:
                rec.timesheet_ids.update({'project_id': rec.project_id.id})

    @api.depends('planned_hours', 'total_hours')
    def _compute_progress_hours(self):
        for rec in self:
            rec.progress = 0.0
            if (rec.planned_hours > 0.0):
                if rec.total_hours > rec.planned_hours:
                    rec.progress = 100
                else:
                    rec.progress = round(
                        100.0 * rec.total_hours / rec.planned_hours, 2
                    )
            rec.remaining_hours = rec.planned_hours - rec.total_hours

    def onchange_planned_hours(self):
        # Change confirmed -> planned
        confirmed_orders = self.filtered(
            lambda x: x.state == 'confirmed' and x.planned_hours > 0
        )
        if confirmed_orders:
            confirmed_orders.write({'state': 'planned'})

        # Change planned -> confirmed
        planned_orders = self.filtered(
            lambda x: x.state == 'planned' and x.planned_hours == 0
        )
        if planned_orders:
            planned_orders.write({'state': 'confirmed'})
