# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PurchaseOrderMerge(models.TransientModel):
    _name = 'stock.warehouse.orderpoint.simulator'
    _description = 'Minimum Stock Rule Simulator'

    origin_orderpoint_id = fields.Many2one(
        'stock.warehouse.orderpoint',
        string='Origin Orderpoint',
        readonly=True,
    )
    product_uom_po_id = fields.Many2one(
        'uom.uom',
        'Purchase Unit of Measure',
        readonly=True,
    )
    product_min_qty = fields.Float(
        'Minimum Quantity',
        digits='Product Unit of Measure',
        required=True,
        help="When the virtual stock goes below the Min Quantity specified for "
        "this field, Odoo generates a procurement to bring the forecasted "
        "quantity to the Max Quantity."
    )
    product_max_qty = fields.Float(
        'Maximum Quantity',
        digits='Product Unit of Measure',
        required=True,
        help="When the virtual stock goes below the Min Quantity, Odoo "
        "generates a procurement to bring the forecasted quantity to the "
        "Quantity specified as Max Quantity."
    )
    qty_multiple = fields.Float(
        'Qty Multiple',
        digits='Product Unit of Measure',
        default=1,
        required=True,
        help="The procurement quantity will be rounded up to this multiple. "
    )
    available_qty = fields.Float(
        'Available Quantity',
        digits='Product Unit of Measure',
    )
    needed_qty = fields.Float(
        'Needed Quantity',
        digits='Product Unit of Measure',
    )
    remaining_qty = fields.Float(
        'Remaining Quantity',
        digits='Product Unit of Measure',
    )
    qty_to_order = fields.Float(
        'Quantity to Order',
        digits='Product Unit of Measure',
    )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        swo = self.env['stock.warehouse.orderpoint']
        sq = self.env['stock.quant']
        stock_location = self.env.ref(
            'stock.stock_location_stock',
            raise_if_not_found=False,
        )

        if active_model == 'stock.warehouse.orderpoint' and active_id:
            origin_orderpoint_id = swo.browse(active_id)[0]
            rec.update(
                {
                    'origin_orderpoint_id':
                        origin_orderpoint_id.id,
                    'product_uom_po_id':
                        origin_orderpoint_id.product_id.uom_po_id.id,
                    'available_qty':
                        sq._get_available_quantity(
                            origin_orderpoint_id.product_id,
                            stock_location,
                        ),
                    'product_min_qty':
                        origin_orderpoint_id.product_min_qty,
                    'product_max_qty':
                        origin_orderpoint_id.product_max_qty,
                    'qty_multiple':
                        origin_orderpoint_id.product_id.uom_po_id.factor_inv,
                }
            )
        return rec

    @api.onchange(
        'available_qty',
        'product_min_qty',
        'product_max_qty',
        'qty_multiple',
    )
    def _onchange_quantity(self):
        self.needed_qty = max(
            self.product_min_qty, self.product_max_qty
        ) - self.available_qty

        if self.qty_multiple > 0:
            self.remaining_qty = self.needed_qty % self.qty_multiple
        else:
            self.remaining_qty = 0.0

        if self.available_qty < self.product_min_qty:
            if self.remaining_qty > 0:
                self.qty_to_order = self.needed_qty + self.qty_multiple - self.remaining_qty
            else:
                self.qty_to_order = self.needed_qty
        else:
            self.qty_to_order = 0

    def action_apply(self):
        for rec in self:
            rec.origin_orderpoint_id.product_min_qty = rec.product_min_qty
            rec.origin_orderpoint_id.product_max_qty = rec.product_max_qty
