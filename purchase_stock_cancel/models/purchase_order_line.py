# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2020

from odoo import _, models
from odoo.tools.misc import formatLang


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_cancellation_message(self):
        return ("%s ⟶ %s × %s") % (
            self.product_id.display_name,
            formatLang(self.env, self.product_qty),
            self.product_uom.display_name,
        )

    def _get_propagation_emoji(self, propagate):
        if propagate == True:
            res = "🚫"
            self.mapped("move_dest_ids").action_cancel_downstream()
        elif propagate == False:
            res = "🗑️"
        return res

    def action_propagate_cancel(self):
        """Note that since Odoo 13.0, there is also a `propagate_cancel` field to handle
        this case, but our downstream cancel action is make the propagation deeper.
        """
        propagate = self.env.context.get("propagate")
        emoji = "?"
        if propagate is True:
            emoji = self._get_propagation_emoji(True)
            self.mapped("move_dest_ids").action_cancel_downstream()
        elif propagate is False:
            emoji = self._get_propagation_emoji(False)
            # if we don't want to propagate the cancellation, then we muste override
            # the odoo built-in value
            self.filtered(lambda line: line.propagate_cancel).write(
                {"propagate_cancel": False}
            )
        # keep a reference on purchase orders
        purchase_orders = self.mapped("order_id")
        # delete all purchase lines, existing move's procure method will be changed
        # to `make_to_stock` via odoo/addons/purchase_stock/models/purchase.py
        # ::PurchaseOrderLine.unlink()
        for line in self:
            msg = _("%s Line deleted: %s") % (emoji, line._get_cancellation_message())
            line.order_id.message_post(body=msg)
            line.unlink()
        # also cancel empty purchase orders
        purchase_orders.filtered(lambda o: not o.order_line).button_cancel()

    def _get_move_notification(self, move):
        """Two possible case:
        - 1) Cancel: The move has been set to `make_to_stock`
        - 2) Cancel and propagate: The move is also cancelled
        """
        if move.state == "cancel":
            res = _(
                "Move <small>%d</small> for <small>%s</small> has also been "
                "<b>cancelled</b> after %s cancellation propagation from <b>%s</b>"
            ) % (
                move.id,
                move.product_id.display_name,
                self._get_propagation_emoji(True),
                self.order_id.display_name,
            )
        elif move.procure_method == "make_to_stock":
            res = _(
                "Procure method of move <small>%d</small> for <small>%s</small> "
                "has been set to «<b>%s</b>» after %s cancellation from <b>%s</b>"
            ) % (
                move.id,
                move.product_id.display_name,
                _("make_to_stock"),
                self._get_propagation_emoji(False),
                self.order_id.display_name,
            )
        return res

    def _get_move_owner(self, move):
        """Get the document (stock.picking/mrp.production) that «owns» this move.
        This method should be inherited in other modules (like `purchase_mrp_cancel`)
        """
        return move.picking_id

    def _notify_move_owner_before_unlink(self):
        notify_messages = {}
        for line in self:
            move_dest_ids = line.move_dest_ids.filtered(
                lambda m: m.state == "cancel"
                or (
                    m.state not in ("cancel", "done")
                    and m.procure_method == "make_to_stock"
                )
            )
            for move in move_dest_ids:
                message = line._get_move_notification(move)
                move_owner_id = self._get_move_owner(move)
                if move_owner_id:
                    if not move_owner_id in notify_messages:
                        notify_messages[move_owner_id] = []
                    notify_messages[move_owner_id].append(message)
        # write a notification on each picking/production
        for move_owner_id, messages in notify_messages.items():
            msg_list = ""
            for m in messages:
                msg_list += "<li>{}</li>".format(m)
            body = _("Some move(s) have changed:")
            body += "<ul>{}</ul>".format(msg_list)
            move_owner_id.message_post(body=body)

    def write(self, vals):
        if vals.get("move_dest_ids") and vals["move_dest_ids"][0][0] == 5:
            self._notify_move_owner_before_unlink()
        res = super().write(vals)
        return res

    def _unlink_from_destination_moves(self):
        """We need to unlink this line from its destination moves to avoid inconsistent
        data. `PurchaseOrder.button_cancel()` does the same thing in
        `addons/purchase_stock/models/purchase.py`
        """
        self.ensure_one()
        move_dest_ids = self.move_dest_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        move_orig_ids = move_dest_ids.mapped("move_orig_ids")
        siblings_states = move_orig_ids.mapped("state")
        if all(s in ("done", "cancel") for s in siblings_states):
            move_dest_ids.write({"procure_method": "make_to_stock"})
            move_dest_ids._recompute_state()

    def unlink(self):
        for line in self.filtered("move_dest_ids"):
            line._unlink_from_destination_moves()
            # note that it is like writing 'created_purchase_line_id': False
            # for each move in move_dest_ids
            line.write({"move_dest_ids": [(5, 0, 0)]})
        return super(PurchaseOrderLine, self).unlink()
