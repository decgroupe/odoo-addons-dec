# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_cancel(self):
        result = super(PurchaseOrder, self).button_cancel()
        self.sudo()._activity_cancel_on_production()
        return result

    def _activity_cancel_on_production(self):
        """If some PO are cancelled, we need to put an activity on their
        origin MO (only the open ones). Since a PO can have been modified
        by several MO, when cancelling one PO, many next activities can
        be schedulded on different MO.
        """
        prod_to_notify_map = (
            {}
        )  # map MO -> recordset of PO as {mrp.production: set(purchase.order.line)}
        for order in self:
            for purchase_line in order.order_line:
                if purchase_line.production_id:
                    prod_to_notify_map.setdefault(
                        purchase_line.production_id, self.env["purchase.order.line"]
                    )
                    prod_to_notify_map[purchase_line.production_id] |= purchase_line

        for production, purchase_lines in prod_to_notify_map.items():
            production._activity_schedule_with_view(
                "mail.mail_activity_data_warning",
                user_id=production.user_id.id or self.env.uid,
                views_or_xmlid="mrp_purchase.exception_mrp_on_purchase_cancellation",
                render_context={
                    "purchase_orders": purchase_lines.mapped("order_id"),
                    "purchase_lines": purchase_lines,
                },
            )
