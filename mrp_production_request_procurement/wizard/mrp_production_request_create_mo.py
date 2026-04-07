# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020

from odoo import models


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.production.request.create.mo"

    def _prepare_manufacturing_order(self):
        """Override to set the procurement group and MO name based on the
        request's common procurement group and production name."""
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
        # use production_name as prefix to generate a manufacturing order with
        # the same name or with an index if waiting quantity > 1
        if request_id.product_qty > 1 or request_id.manufactured_qty > 0:
            mo_idx = round(request_id.manufactured_qty) + 1
            res["name"] = f"{request_id.production_name}/{mo_idx:02d}"
        else:
            res["name"] = request_id.production_name
        return res


class MrpProductionRequestCreateMoLine(models.TransientModel):
    _inherit = "mrp.production.request.create.mo.line"
