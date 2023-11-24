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

    def action_propagate_cancel(self):
        """Note that since Odoo 13.0, there is also a `propagate_cancel` field to handle
        this case, but our downstream cancel action is make the propagation deeper.
        """
        propagate = self.env.context.get("propagate")
        emoji = "?"
        if propagate is True:
            emoji = "🚫"
            self.mapped("move_dest_ids").action_cancel_downstream()
        elif propagate is False:
            emoji = "🗑️"
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
        res = _(
            "Procure method of move <small>%s</small> for <small>%s</small> "
            "has been set to «<b>%s</b>» after cancellation from <b>%s</b>"
        ) % (
            move.id,
            move.product_id.display_name,
            _("make_to_stock"),
            self.order_id.display_name,
        )
        return res

    def _notify_pickings_before_unlink(self):
        notify_messages = {}
        for line in self:
            move_dest_ids = line.move_dest_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
                and m.procure_method == "make_to_stock"
            )
            for move in move_dest_ids:
                message = line._get_move_notification(move)
                if not move.picking_id in notify_messages:
                    notify_messages[move.picking_id] = []
                notify_messages[move.picking_id].append(message)

        # Write a notification on each picking
        for picking_id, messages in notify_messages.items():
            msg_list = ""
            for m in messages:
                msg_list += "<li>{}</li>".format(m)
            body = _("Some move(s) have changed:")
            body += "<ul>{}</ul>".format(msg_list)
            picking_id.message_post(body=body)

    def write(self, vals):
        if vals.get("move_dest_ids") and vals["move_dest_ids"][0][0] == 5:
            self._notify_pickings_before_unlink()
        res = super().write(vals)
        return res

    def unlink(self):
        for line in self:
            if line.move_dest_ids:
                # We need to unlink this line from its destination moves to
                # avoid inconsistent data.
                # Note that Purchase Order cancelation does the same thing in
                # button_cancel()
                # addons/purchase_stock/models/purchase.py
                move_dest_ids = line.move_dest_ids.filtered(
                    lambda m: m.state not in ("done", "cancel")
                )
                move_orig_ids = move_dest_ids.mapped("move_orig_ids")
                siblings_states = move_orig_ids.mapped("state")
                if all(s in ("done", "cancel") for s in siblings_states):
                    move_dest_ids.write({"procure_method": "make_to_stock"})
                    move_dest_ids._recompute_state()

            # Note that it is like writing 'created_purchase_line_id': False
            # for each move in move_dest_ids
            line.write({"move_dest_ids": [(5, 0, 0)]})

        return super(PurchaseOrderLine, self).unlink()
