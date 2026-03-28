# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020

from odoo import models


class MrpProductionRequest(models.Model):
    _inherit = "mrp.production.request"

    def create_all_manufacturing_orders(self):
        """Create one manufacturing order of qty 1 for each pending unit."""
        for _idx in range(0, round(self.pending_qty)):
            wizard = (
                self.with_context(
                    active_model=self._name,
                    active_ids=self.ids,
                    active_id=self.id,
                )
                .env["mrp.production.request.create.mo"]
                .create({})
            )
            wizard.mo_qty = 1
            wizard.create_mo()
