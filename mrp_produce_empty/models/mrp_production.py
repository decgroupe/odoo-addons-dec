# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020


from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _compute_state(self):
        other_mos = self.env["mrp.production"]
        for production in self:
            if production.product_id and not production.move_raw_ids and all(
                move.state in ("cancel", "done")
                for move in production.move_finished_ids
            ):
                production.state = "done"
                production.reservation_state = "assigned"
            else:
                other_mos += production
        super(MrpProduction, other_mos)._compute_state()

    def action_confirm(self):
        self._check_company()
        mo_to_confirm = self.env["mrp.production"]
        for production in self:
            if not production.move_raw_ids:
                production.qty_producing = production.product_qty
                production.move_finished_ids._action_confirm()
                for move in production.move_finished_ids:
                    move.quantity_done = move.product_uom_qty
                production.move_finished_ids._action_done()
            else:
                mo_to_confirm += production
        return super(MrpProduction, mo_to_confirm).action_confirm()
