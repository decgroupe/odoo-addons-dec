# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2020

from odoo import _, api, models
from odoo.tools.misc import formatLang, format_date


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
