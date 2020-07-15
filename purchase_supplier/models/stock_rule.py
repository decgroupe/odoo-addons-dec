# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Jul 2020

from odoo import api, fields, models, _


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _make_po_select_supplier(self, values, suppliers):
        selected_supplier = super()._make_po_select_supplier(values, suppliers)
        move_dest_ids = values.get('move_dest_ids')
        if move_dest_ids:
            move_id = move_dest_ids[0]
            if move_id.bom_line_id and move_id.bom_line_id.partner_id:
                for supplier in suppliers:
                    if supplier.name.id == move_id.bom_line_id.partner_id.id:
                        selected_supplier = supplier
                        break
        return selected_supplier
