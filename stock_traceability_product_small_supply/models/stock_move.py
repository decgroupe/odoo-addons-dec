# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_pre_header(self):
        if (
            self.product_id.small_supply
            and self.product_id.type == "consu"
            and self.product_id.is_storable
        ):
            # Translate field name to display string
            IrModelFields = self.env["ir.model.fields"]
            small_supply_field_name = IrModelFields.get_field_string(
                self.product_id._name
            )["small_supply"]
            head = f"⛽{small_supply_field_name}"
        else:
            head = super()._get_pre_header()
        return head
