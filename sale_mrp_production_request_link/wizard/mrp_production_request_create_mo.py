# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo import models


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.production.request.create.mo"

    def _prepare_manufacturing_order(self):
        vals = super()._prepare_manufacturing_order()
        request_id = self.mrp_production_request_id
        if request_id.sale_order_id:
            vals["sale_order_id"] = request_id.sale_order_id.id
        return vals