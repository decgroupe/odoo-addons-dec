# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Apr 2020

from odoo import models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def unlink(self):
        for line in self:
            if line.move_dest_ids:
                # We need to unlink this line from its destination moves to
                # avoid inconsistent data.
                # Note that Purchase Order cancelation does the same thing in
                # button_cancel()
                # addons/purchase_stock/models/purchase.py
                move_dest_ids = line.move_dest_ids.filtered(
                    lambda m: m.state not in ('done', 'cancel')
                )
                move_orig_ids = move_dest_ids.mapped('move_orig_ids')
                siblings_states = move_orig_ids.mapped('state')
                if all(s in ('done', 'cancel') for s in siblings_states):
                    move_dest_ids.write(
                        {
                            'procure_method': 'make_to_stock',
                            'created_purchase_line_id': False,
                        }
                    )
                    move_dest_ids._recompute_state()
        return super(PurchaseOrderLine, self).unlink()
