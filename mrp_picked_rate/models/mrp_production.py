# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from datetime import timedelta
from odoo import api, models, _, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    supply_progress = fields.Float(
        compute='_compute_supply_progress',
        oldname='picked_rate',
        help='Rate of received raw products',
        store=True,
    )

    kanban_show_supply_progress = fields.Boolean(
        string="Show Supply Progress",
        compute="_compute_kanban_show_supply_progress",
    )

    @api.multi
    @api.depends('move_raw_ids', 'note')
    def _compute_supply_progress(self):
        for rec in self:
            if not rec.move_raw_ids:
                rec.supply_progress = 100
            else:
                all_move_ids = rec.move_raw_ids.filtered(
                    lambda x: x.state != 'cancel'
                )
                if all_move_ids:
                    received_move_ids = all_move_ids.filtered(
                        lambda x: x.received
                    )
                    rec.supply_progress = \
                        len(received_move_ids) * 100 / len(all_move_ids)

    @api.multi
    def action_update_supply_progress(self):
        self._compute_supply_progress()

    @api.multi
    def run_supply_progress_update_scheduler(self):
        date = fields.Datetime.to_string(
            fields.datetime.now() - timedelta(days=365)
        )
        production_ids = self.search(
            [
                ('supply_progress', '<', 100),
                ('write_date', '>=', date),
                ('state', '!=', 'cancel'),
            ]
        ).filtered('move_raw_ids')
        production_ids._compute_supply_progress()

    def _get_stages_ref(self):
        res = super()._get_stages_ref()
        res['supplying'] = self.env.ref('mrp_picked_rate.stage_supplying')
        return res

    @api.multi
    @api.depends('supply_progress')
    def _compute_stage_id(self):
        super()._compute_stage_id()
        stages = self._get_stages_ref()
        for rec in self:
            if rec.stage_id == stages['confirmed'] and rec.supply_progress > 0:
                rec.stage_id = stages['supplying']

    @api.multi
    @api.depends('stage_id', 'supply_progress')
    def _compute_kanban_show_supply_progress(self):
        stages = self._get_stages_ref()
        for rec in self:
            if not rec.move_raw_ids:
                rec.kanban_show_purchase_progress = False
            elif rec.stage_id.id == stages['supplying'].id:
                rec.kanban_show_supply_progress = True
            elif rec.supply_progress < 100 and rec.stage_id.id in (
                stages['progress'].id, stages['issue'].id
            ):
                rec.kanban_show_supply_progress = True
