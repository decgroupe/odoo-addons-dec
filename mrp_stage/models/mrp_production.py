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

    def _get_stage_from_activity(self):
        self.ensure_one()
        activity_ids = self.activity_ids
        res = False
        for activity_id in activity_ids:
            if activity_id.activity_type_id.production_stage_id:
                seq = activity_id.activity_type_id.production_stage_id.sequence
                if not res or seq > res.sequence:
                    res = activity_id.activity_type_id
        if res:
            res = res.production_stage_id
        return res

    def _get_stage_from_state(self, stages):
        self.ensure_one()
        stage_id = False
        if self.state in stages:
            stage_id = stages[self.state]
        if self.state in ('confirmed', 'planned', 'progress'):
            activity_stage_id = self._get_stage_from_activity()
            if activity_stage_id:
                stage_id = activity_stage_id
        elif self.state == 'done':
            move_finished_ids = self.move_finished_ids.filtered(
                lambda x: x.state in ('done', 'cancel')
            )
            picking_move_ids = move_finished_ids.mapped('move_dest_ids')
            if not all(
                m.state in ('done', 'cancel') for m in picking_move_ids
            ):
                stage_id = stages['dispatch_ready']
        return stage_id

    @api.multi
    @api.depends(
        'state', 'activity_ids', 'activity_ids.state',
        'move_finished_ids.move_dest_ids.state'
    )
    def _compute_stage_id(self):
        stages = self._get_stages_ref()
        for rec in self:
            stage_id = rec._get_stage_from_state(stages)
            if stage_id:
                rec.stage_id = stage_id

    @api.multi
    def action_recompute_stage_id(self):
        self._compute_stage_id()

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

    @api.multi
    def _allow_auto_start(self):
        self.ensure_one()
        return self.state in ('planned', 'confirmed')

    @api.multi
    def action_view_staged(self):
        action = self.env.ref('mrp_stage.act_mrp_production_staged').read()[0]
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            action['domain'] = [('id', 'in', self.ids)]
        else:
            action['views'] = [
                (self.env.ref('mrp.mrp_production_form_view').id, 'form')
            ]
            action['res_id'] = self.id
        return action

    @api.model
    def action_view_staged_with_products(self, product_ids):
        action = self.env.ref('mrp_stage.act_mrp_production_staged').read()[0]
        action["domain"] = [("product_id", "in", product_ids)]
        action["context"] = {}
        return action
