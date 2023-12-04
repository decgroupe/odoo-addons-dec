# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MrpAttachPicking(models.TransientModel):
    _name = "mrp.attach.picking"
    _description = "Attach production order to picking"

    production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Production Order",
        required=True,
        readonly=True,
        domain=[],
    )
    product_id = fields.Many2one(
        related="production_id.product_id",
        string="Product",
        required=True,
        readonly=True,
    )
    product_uom_qty = fields.Float(
        related="production_id.product_uom_qty",
    )
    move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Move",
        required=True,
    )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_id = self._context.get("active_id")
        active_model = self._context.get("active_model")

        if active_model == "mrp.production" and active_id:
            production_id = self.env["mrp.production"].browse(active_id)
            # Assign wizard default values
            product_id = production_id.mapped("product_id")
            rec.update(
                {
                    "production_id": production_id.id,
                    "product_id": product_id.id,
                }
            )
        return rec

    def do_attach(self):
        self.ensure_one()
        # Filter finished move in case of some of them are cancelled
        move_finished_ids = self.production_id.move_finished_ids.filtered(
            lambda x: x.state in ("confirmed", "assigned", "done")
        )
        if not move_finished_ids:
            raise ValidationError(
                _("None of the production finished moves can be linked.")
            )
        # write procure method and recompute state BEFORE assigning a parent move to
        # ensure a `waiting` state
        self.move_id.write({"procure_method": "make_to_order"})
        self.move_id._recompute_state()
        # link chosen move with our production order
        self.move_id.write({"move_orig_ids": [(6, 0, move_finished_ids.ids)]})
        self.move_id._recompute_state()
        # also try to assign in the case the parent move is already done
        self.move_id._action_assign()
