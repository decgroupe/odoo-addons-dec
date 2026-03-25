# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        """Add `supplierinfo_id` to procurement values if the move is linked to a BoM
        line with a supplier. (note that in previous versions, this was previously done
        in `_make_po_select_supplier` from `stock.rule` model when executing `_run_buy`)
        """
        res = super()._prepare_procurement_values()
        if self.bom_line_id and self.bom_line_id.partner_id:
            res["supplierinfo_id"] = self.bom_line_id.seller_id
        return res
