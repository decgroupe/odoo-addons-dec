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
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Apr 2020

from odoo import fields, models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def unlink(self):
        for line in self:
            if line.move_dest_ids:
                move_dest_ids = line.move_dest_ids
                line.move_dest_ids.write(
                    {
                        'procure_method': 'make_to_stock',
                        'created_purchase_line_id': False,
                    }
                )
                move_dest_ids._recompute_state()
        return super(PurchaseOrderLine, self).unlink()
