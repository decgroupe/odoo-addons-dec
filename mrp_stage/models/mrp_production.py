# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2022

from datetime import datetime

from odoo import api, models, _, fields, SUPERUSER_ID


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # Add index to speed-up search
    bom_id = fields.Many2one(index=True)

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        return self.env.ref(
            'mrp_stage.stage_confirmed', raise_if_not_found=False
        )

    stage_id = fields.Many2one(
        comodel_name='mrp.production.stage',
        string='Stage',
        ondelete='set null',
        default=_get_default_stage_id,
        compute='_compute_stage_id',
        track_visibility='onchange',
        index=True,
        store=True,
        copy=False,
    )

    stage_todo = fields.Boolean(
        string="To-do",
        related='stage_id.todo',
        help="Used as a filter to only display production order linked to "
        "stages with to-do actions",
        index=True,
        store=True,
    )

    # For Kanban
    kanban_color = fields.Integer(string='Color Index')

    @api.model
    def _get_stages_ref(self):
        return {
            'confirmed': self.env.ref('mrp_stage.stage_confirmed'),
            'planned': self.env.ref('mrp_stage.stage_planned'),
            'progress': self.env.ref('mrp_stage.stage_progress'),
            'issue': self.env.ref('mrp_stage.stage_issue'),
            'dispatch_ready': self.env.ref('mrp_stage.stage_dispatch_ready'),
            'done': self.env.ref('mrp_stage.stage_done'),
            'cancel': self.env.ref('mrp_stage.stage_cancel'),
        }

    @api.model
    def _get_issue_activity(self):
        return self.env.ref('mrp_stage.mail_activity_production_issue')

    @api.multi
    @api.depends('state', 'activity_ids', 'activity_ids.state')
    def _compute_stage_id(self):
        activity_type_issue = self._get_issue_activity()
        stages = self._get_stages_ref()
        for rec in self:
            if rec.state in stages:
                rec.stage_id = stages[rec.state]
            if rec.state in ('confirmed', 'planned', 'progress'):
                if rec.activity_ids.filtered(
                    lambda x: x.activity_type_id.id == activity_type_issue.id
                ):
                    rec.stage_id = stages['issue']
            elif rec.state == 'done':
                move_finished_ids = self.move_finished_ids.filtered(
                    lambda x: x.state in ('done', 'cancel')
                )
                picking_move_ids = move_finished_ids.mapped('move_dest_ids')
                if not all(
                    m.state in ('done', 'cancel') for m in picking_move_ids
                ):
                    rec.stage_id = stages['dispatch_ready']

    def action_assign_to_me(self):
        self.write({
            'user_id': self.env.user.id,
        })

    @api.multi
    def action_start(self):
        self.ensure_one()
        if self.state in ('done', 'cancel'):
            return True
        self.write({
            'state': 'progress',
            'date_start': datetime.now(),
        })
        # OCA module needed: web_ir_actions_act_view_reload
        return {
            'type': 'ir.actions.act_view_reload',
        }
