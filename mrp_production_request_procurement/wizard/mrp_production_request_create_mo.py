# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020

from odoo import models


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.production.request.create.mo"

    def _prepare_manufacturing_order(self):
        self.ensure_one()
        res = super()._prepare_manufacturing_order()
        request_id = self.mrp_production_request_id

        if request_id.use_common_procurement_group:
            # Assign existing common group
            res["procurement_group_id"] = request_id.common_procurement_group_id.id
        else:
            # Remove default procurement since using an existing SOxxxx group
            # can lead to side effects (all pickings cancelled)
            # https://github.com/OCA/manufacture/issues/516
            res["procurement_group_id"] = False

        # Use production_name as prefix to generate a manufacturing order with
        # the same name or with an index if waiting quantity > 1
        if request_id.product_qty > 1 or request_id.manufactured_qty > 0:
            res["name"] = "{0}/{1:02d}".format(
                request_id.production_name,
                round(request_id.manufactured_qty) + 1,
            )
        else:
            res["name"] = request_id.production_name
        return res

    def create_mo(self):
        self.ensure_one()
        action = super().create_mo()
        mo = self.env["mrp.production"].browse(action["res_id"])
        return action


class MrpProductionRequestCreateMoLine(models.TransientModel):
    _inherit = "mrp.production.request.create.mo.line"
