# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2022

from datetime import datetime

from odoo import api, models, _, fields, SUPERUSER_ID


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        return self.env.ref(
            'mrp_stage.stage_confirmed', raise_if_not_found=False
        )

    stage_id = fields.Many2one(
        comodel_name='mrp.production.stage',
        string='Stage',
        ondelete='restrict',
        track_visibility='onchange',
        index=True,
        default=_get_default_stage_id,
        copy=False,
        compute='_compute_stage_id',
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

    def action_assign_to_me(self):
        self.write({
            'user_id': self.env.user.id,
        })

    @api.multi
    def action_start(self):
        self.ensure_one()
        if self.state in ('done', 'cancel'):
            return True
        self.write(
            {
                'state': 'progress',
                'date_start': datetime.now(),
            }
        )
        # OCA module needed: web_ir_actions_act_view_reload
        return {
            'type': 'ir.actions.act_view_reload',
        }