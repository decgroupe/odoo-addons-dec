# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    production_request_ids = fields.One2many(
        comodel_name="mrp.production.request",
        inverse_name="sale_order_id",
        string="Manufacturing Requests",
    )
    production_request_count = fields.Integer(
        compute="_compute_production_request_count",
        store=True,
        string="Number of Manufacturing Requests",
    )

    @api.depends("production_request_ids")
    def _compute_production_request_count(self):
        for sale in self:
            sale.production_request_count = len(sale.production_request_ids)

    def action_view_production_request(self):
        action = self.mapped("production_request_ids").action_view()
        return action

    def action_cancel(self):
        result = super(SaleOrder, self).action_cancel()
        # When a sale person cancel a SO, he might not have the rights to write
        # on MR. But we need the system to create an activity on the MR (so
        # 'write' access), hence the `sudo`.
        self.sudo()._activity_cancel_on_production_request()
        return result

    def _activity_cancel_on_production_request(self):
        """If some SO are cancelled, we need to put an activity on their
        generated production requests. We only want one activity to
        be attached.
        """
        for production_request in self.mapped("production_request_ids"):
            if (
                production_request.state in ("draft", "to_approve")
                and not production_request.mrp_production_ids
            ):
                production_request.button_cancel()
                production_request.message_post(
                    body=_(
                        "Automatic cancellation following cancellation of the sell "
                        "order"
                    )
                )
            else:
                production_request._activity_schedule_with_view(
                    "mail.mail_activity_data_warning",
                    user_id=production_request.assigned_to.id
                    or production_request.requested_by.id
                    or self.env.uid,
                    views_or_xmlid="sale_mrp_production_request_link."
                    "exception_production_request_on_sale_cancellation",
                    render_context={
                        "sale_orders": self,
                    },
                )
