# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2020

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_raw_move_data(self, bom_line, line_data):
        res = super(MrpProduction, self)._get_raw_move_data(bom_line, line_data)
        if res is not None:
            # Link move destination to production moves to-do, this hook is
            # only done to keep REF Manager stock.move compatibility with
            # legacy way (from OpenERP)
            res["move_dest_ids"] = [(6, 0, self.move_finished_ids.ids)]
        return res
