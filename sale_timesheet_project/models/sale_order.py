# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Field initially defined in `sale_project` module
    project_id = fields.Many2one(
        copy=False,
    )

    def _action_confirm(self):
        self.action_create_project()
        res = super(SaleOrder, self)._action_confirm()
        self._sync_project()
        return res

    def _sync_project(self):
        for rec in self.filtered("project_id"):
            rec.project_id.sudo().write(
                {
                    # when billable is enabled, a sale order should be provided to
                    # ensure valid data from tasks. This value should be set only when
                    # the quotation is converted to a sale order
                    "sale_order_id": self.id,
                    # sync dates
                    "date_start": rec.date_order.date(),
                    "date": rec.expected_last_date and rec.expected_last_date.date(),
                }
            )

    def _get_create_project_data(self):
        self.ensure_one()
        contract_type_id = self.env.ref("project_identification.contract_type")
        return {
            "name": self.name,
            # Use the same partner than the sale order. The shipping
            # partner is retrieved using `project_partner_location`
            # module and the `partner_shipping_id` field.
            "partner_id": self.partner_id.id,
            "type_id": contract_type_id.id,
            "user_id": self.user_id.id,
            # `allow_timesheets` default is already True from
            # hr_timesheet/models/project.py
            "allow_timesheets": True,
            # force billable to ensure proper `qty_delivered` computation on sale oder
            # lines, otherwise `so_line` will not be computed properly on analytic
            # account lines
            "allow_billable": True,
            "bill_type": "customer_project",
            "pricing_type": "fixed_rate",
        }

    def action_create_project(self):
        Project = self.env["project.project"].with_context(
            # Do not subscribe assigned user
            mail_create_nosubscribe=True,
            # Do not notify the subscribed user (not needed if
            # `mail_create_nosubscribe=True`)
            mail_auto_subscribe_no_notify=True,
        )
        for rec in self:
            if not rec.project_id or self.env.context.get("override_project_id"):
                project_data = rec._get_create_project_data()
                domain = [("name", "=", project_data["name"])]
                if not self.env.context.get("ignore_partner_id"):
                    domain += [("partner_id", "=", project_data["partner_id"])]
                project_id = Project.with_context(
                    active_test=False,
                ).search(domain, limit=1)
                if not project_id:
                    # Create project as SUPER_USER
                    project_id = Project.sudo().create(project_data)
                rec.project_id = project_id
                self.env.add_to_compute(project_id._fields["contract_ids"], project_id)
                # rec.write({"project_id": project_id.id})
                # project_id.recompute()
            # Assign same analytic account
            rec.analytic_account_id = rec.project_id.analytic_account_id

    @api.depends("project_id")
    def _compute_visible_project(self):
        super()._compute_visible_project()
        for order in self.filtered(lambda x: not x.visible_project):
            # override builtin logic to always display existing projects
            if order.project_id:
                order.visible_project = True
