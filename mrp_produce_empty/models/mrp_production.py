# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020


from odoo import _, api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends(
        "move_raw_ids.state", "workorder_ids.move_raw_ids", "bom_id.ready_to_produce"
    )
    def _compute_availability(self):
        super()._compute_availability()
        for order in self:
            if not order.move_raw_ids:
                # Override availability from 'none' (min) to 'assigned' (max)
                # This will allow us to display the 'Produce' button
                order.availability = "assigned"
                continue
