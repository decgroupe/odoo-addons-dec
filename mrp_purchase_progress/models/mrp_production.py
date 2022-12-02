# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from datetime import timedelta
from odoo import api, models, _, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    purchase_progress = fields.Float(
        compute='_compute_purchase_progress',
        help='Rate of products already purchased',
        store=True,
    )

    kanban_show_purchase_progress = fields.Boolean(
        string="Show Purchase Progress",
        compute="_compute_kanban_show_purchase_progress",
    )

    @api.depends('move_raw_ids', 'move_raw_ids.state')
    def _compute_purchase_progress(self):
        for rec in self:
            if not rec.move_raw_ids:
                rec.purchase_progress = 100
            else:
                all_move_ids = rec.move_raw_ids.filtered(
                    lambda x: \
                        x.state != 'cancel' \
                        and x.procure_method == 'make_to_order' \
                        and x.created_purchase_line_id.id
                )
                if all_move_ids:
                    purchased_move_ids = all_move_ids.mapped(
                        'move_orig_ids'
                    ).filtered(lambda x: x.state in ('assigned', 'done'))
                    ready_move_ids = purchased_move_ids.mapped('move_dest_ids')
                    rec.purchase_progress = \
                        len(ready_move_ids) * 100 / len(all_move_ids)

    def action_update_purchase_progress(self):
        self._compute_purchase_progress()

    def run_purchase_progress_update_scheduler(self):
        date = fields.Datetime.to_string(
            fields.datetime.now() - timedelta(days=365)
        )
        production_ids = self.search(
            [
                ('purchase_progress', '<', 100),
                ('write_date', '>=', date),
                ('state', '!=', 'cancel'),
            ]
        ).filtered('move_raw_ids')
        production_ids._compute_purchase_progress()

    def _is_supply_active(self):
        res = super()._is_supply_active()
        res = res or self.purchase_progress > 0
        return res

    @api.depends('purchase_progress')
    def _compute_stage_id(self):
        return super()._compute_stage_id()

    @api.depends('stage_id', 'purchase_progress')
    def _compute_kanban_show_purchase_progress(self):
        stages = self._get_stages_ref()
        for rec in self:
            if not rec.move_raw_ids:
                rec.kanban_show_purchase_progress = False
            elif rec.stage_id.id == stages['supplying'].id:
                rec.kanban_show_purchase_progress = True
            elif rec.purchase_progress < 100 and rec.stage_id.id in (
                stages['progress'].id, stages['issue'].id
            ):
                rec.kanban_show_purchase_progress = True
