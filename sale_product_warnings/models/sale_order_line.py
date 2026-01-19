# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        res = super()._onchange_product_id_warning()

        if self.product_id:
            warning = {
                "title": self.env._("Warning for %s") % self.product_id.name,
            }

            description = self.product_id.description or self.env._("No internal notes")
            responsible = (
                self.product_id.responsible_id
                and self.product_id.responsible_id.name
                or self.env._("No responsible for this product")
            )

            if self.product_id.state == "obsolete":
                warning["message"] = self.env._(
                    "Obsolete product!\n "
                    "(This product must not be sold anymore.)\n\n %(description)s",
                    description=description,
                )
            elif self.product_id.state == "review":
                warning["message"] = self.env._(
                    "This product needs to be reviewed:\n\n - %(description)s \n\n - "
                    'Please contact "%(responsible)s"',
                    description=description,
                    responsible=responsible,
                )
            elif self.product_id.state == "quotation":
                warning["message"] = self.env._(
                    "This product is currently in quotation, prices may "
                    "not be correct:\n\n - %(description)s \n\n - "
                    'You can take contact with "%(responsible)s"',
                    description=description,
                    responsible=responsible,
                )
            else:
                warning = False

            if warning:
                res = {"warning": warning}
        return res

    @api.model_create_multi
    def create(self, vals_list):
        record_ids = super().create(vals_list)
        for rec, _vals in zip(record_ids, vals_list, strict=True):
            if rec.product_id.state == "review":
                rec._schedule_review_activity()
        return record_ids

    def _schedule_review_activity(self):
        self.ensure_one()
        order_state = dict(
            self.order_id._fields["state"]._description_selection(self.env)
        ).get(self.order_id.state)
        self.order_id.with_context(
            mail_activity_noautofollow=True
        )._activity_schedule_with_view(
            "sale_product_warnings.mail_activity_data_review",
            user_id=self.product_id.responsible_id.id
            or self.order_id.user_id.id
            or self.env.uid,
            views_or_xmlid="sale_product_warnings.exception_product_review",
            render_context={
                "product_id": self.product_id,
                "product_state": self.product_id.product_state_id.name,
                "order_id": self.order_id,
                "order_state": order_state,
            },
        )
