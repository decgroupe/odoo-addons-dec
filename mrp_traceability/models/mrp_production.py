# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2020

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        # Update finished moves or they will be named « New »
        if vals.get("move_finished_ids"):
            rec.move_finished_ids.write({"name": rec.name})
        # Update raw moves or they will be named « New »
        if vals.get("move_raw_ids"):
            rec.move_raw_ids.write({"name": rec.name})
        rec._update_raw_move_conv_dest_ids(vals)
        return rec

    def write(self, vals):
        res = super().write(vals)
        self._update_raw_move_conv_dest_ids(vals)
        return res

    def _update_raw_move_conv_dest_ids(self, vals=None):
        """Link move destination to production moves to-do to improve traceability with
        some custom tools.
        """
        if not vals or vals.get("move_finished_ids") or vals.get("move_raw_ids"):
            for rec in self:
                if rec.move_finished_ids.ids and rec.move_raw_ids.ids:
                    rec.move_raw_ids.write(
                        {"move_conv_dest_ids": [(6, 0, self.move_finished_ids.ids)]}
                    )
