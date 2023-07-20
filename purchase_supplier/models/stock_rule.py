# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_select_supplier(self, values, suppliers):
        selected_supplier = super()._make_po_select_supplier(values, suppliers)
        move_dest_ids = values.get("move_dest_ids")
        if move_dest_ids:
            move_id = move_dest_ids[0]
            if move_id.bom_line_id and move_id.bom_line_id.partner_id:
                for supplier in suppliers:
                    if supplier.name.id == move_id.bom_line_id.partner_id.id:
                        selected_supplier = supplier
                        break
        return selected_supplier
