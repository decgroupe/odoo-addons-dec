# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import api, fields, models


class PurchaseOrderMerge(models.TransientModel):
    _name = "stock.warehouse.orderpoint.simulator"
    _description = "Minimum Stock Rule Simulator"

    origin_orderpoint_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint",
        string="Origin Orderpoint",
        readonly=True,
    )
    product_uom_po_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Purchase Unit of Measure",
        readonly=True,
    )
    product_min_qty = fields.Float(
        string="Minimum Quantity",
        digits="Product Unit of Measure",
        required=True,
        help="When the virtual stock goes below the Min Quantity specified for "
        "this field, Odoo generates a procurement to bring the forecasted "
        "quantity to the Max Quantity.",
    )
    product_max_qty = fields.Float(
        string="Maximum Quantity",
        digits="Product Unit of Measure",
        required=True,
        help="When the virtual stock goes below the Min Quantity, Odoo "
        "generates a procurement to bring the forecasted quantity to the "
        "Quantity specified as Max Quantity.",
    )
    qty_multiple = fields.Float(
        string="Qty Multiple",
        digits="Product Unit of Measure",
        default=1,
        required=True,
        help="The procurement quantity will be rounded up to this multiple. ",
    )
    available_qty = fields.Float(
        string="Available Quantity",
        digits="Product Unit of Measure",
    )
    needed_qty = fields.Float(
        string="Needed Quantity",
        digits="Product Unit of Measure",
    )
    remaining_qty = fields.Float(
        string="Remaining Quantity",
        digits="Product Unit of Measure",
        compute="_compute_qty",
    )
    qty_to_order = fields.Float(
        string="Quantity to Order",
        digits="Product Unit of Measure",
        compute="_compute_qty",
    )

    @api.model_create_multi
    def create(self, vals_list):
        record_ids = super().create(vals_list)
        record_ids._compute_qty()
        return record_ids

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_id = self._context.get("active_id")
        active_model = self._context.get("active_model")
        swo = self.env["stock.warehouse.orderpoint"]
        quant = self.env["stock.quant"]
        stock_location = self.env.ref(
            "stock.stock_location_stock",
            raise_if_not_found=False,
        )

        if active_model == "stock.warehouse.orderpoint" and active_id:
            # origin orderpoint
            oo_id = swo.browse(active_id)[0]
            rec.update(
                {
                    "origin_orderpoint_id": oo_id.id,
                    "product_uom_po_id": oo_id.product_id.uom_po_id.id,
                    "available_qty": quant._get_available_quantity(
                        oo_id.product_id,
                        stock_location,
                    ),
                    "product_min_qty": oo_id.product_min_qty,
                    "product_max_qty": oo_id.product_max_qty,
                    "qty_multiple": oo_id.product_id.uom_po_id.factor_inv,
                }
            )
        return rec

    @api.depends(
        "available_qty",
        "product_min_qty",
        "product_max_qty",
        "qty_multiple",
    )
    def _compute_qty(self):
        self.needed_qty = (
            max(self.product_min_qty, self.product_max_qty) - self.available_qty
        )

        if self.qty_multiple > 0:
            self.remaining_qty = self.needed_qty % self.qty_multiple
        else:
            self.remaining_qty = 0.0

        if self.available_qty < self.product_min_qty:
            if self.remaining_qty > 0:
                self.qty_to_order = (
                    self.needed_qty + self.qty_multiple - self.remaining_qty
                )
            else:
                self.qty_to_order = self.needed_qty
        else:
            self.qty_to_order = 0

    def action_apply(self):
        for rec in self:
            rec.origin_orderpoint_id.product_min_qty = rec.product_min_qty
            rec.origin_orderpoint_id.product_max_qty = rec.product_max_qty
