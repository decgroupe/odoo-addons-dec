# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020

from odoo import api, fields, models, _


class MrpProductionRequest(models.Model):
    _inherit = "mrp.production.request"

    def create_all_manufacturing_orders(self):
        for idx in range(0, round(self.pending_qty)):
            context = self.env.context.copy()
            context.update(
                {
                    "active_model": self._name,
                    "active_ids": self.ids,
                    "active_id": self.id,
                }
            )
            wizard = (
                self.with_context(context)
                .env["mrp.production.request.create.mo"]
                .create({})
            )
            wizard.mo_qty = 1
            wizard.create_mo()
