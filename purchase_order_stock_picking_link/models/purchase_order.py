# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    outgoing_picking_ids = fields.One2many(
        comodel_name="stock.picking",
        compute="_compute_outgoing_picking",
    )
    outgoing_picking_count = fields.Integer(
        compute="_compute_outgoing_picking",
        string="Picking count",
        default=0,
        store=False,
    )

    def _compute_outgoing_picking(self):
        for order in self:
            order.outgoing_picking_ids = order.order_line.mapped(
                "move_dest_ids"
            ).mapped("picking_id")
            order.outgoing_picking_ids -= order.picking_ids
            order.outgoing_picking_count = len(order.outgoing_picking_ids)

    def action_view_outgoing_picking(self):
        """This function returns an action that display existing outgoing
        picking of given purchase order ids. When only one found, show the
        picking immediately.
        Note that it is a copycat of action_view_picking from
            'addons/purchase_stock/models/purchase.py'
        """
        action = self.env.ref("stock.action_picking_tree_all")
        result = action.read()[0]
        # override the context to get rid of the default filtering on
        # operation type
        result["context"] = {}
        pick_ids = self.mapped("outgoing_picking_ids")
        # choose the view_mode accordingly
        if not pick_ids or len(pick_ids) > 1:
            result["domain"] = "[('id', 'in', %s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref("stock.view_picking_form", False)
            form_view = [(res and res.id or False, "form")]
            if "views" in result:
                result["views"] = form_view + [
                    (state, view) for state, view in result["views"] if view != "form"
                ]
            else:
                result["views"] = form_view
            result["res_id"] = pick_ids.id
        return result
