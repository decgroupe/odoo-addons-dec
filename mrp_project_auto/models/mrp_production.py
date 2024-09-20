# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not self.env.context.get("mrp_project_auto_disable"):
                # Project must be created before any moves to be propagated
                # to sub-production. It Odoo 12.0, it was previously done in a
                # `_generate_moves` function but all this code has been refactored.
                project_id = self._create_or_retrieve_project(vals)
                if project_id:
                    vals.update(
                        {
                            "project_id": project_id.id,
                            "allow_timesheets": True,
                        }
                    )
        production_ids = super(MrpProduction, self).create(vals_list)
        return production_ids

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        return res

    @api.model
    def _create_or_retrieve_project(self, data):
        """Use record or create data to findout if we have to create a new project
        or reuse an existing one. The returned value will be the newly created project
        record.
        """
        if not data.get("project_id") or self.env.context.get("override_project_id"):
            project_data = self._get_project_data(data)
            project_id = self.env["project.project"].search(
                [
                    ("name", "=", project_data["name"]),
                    ("partner_id", "=", project_data["partner_id"]),
                ],
                limit=1,
            )
            if not project_id:
                project_id = self._create_project(project_data)
            return project_id
        return None

    @api.model
    def _create_project(self, data):
        # Create project as SUPER_USER
        project_id = self.env["project.project"].sudo().create(data)
        return project_id

    @api.model
    def _get_project_data(self, data):
        time_tracking_type_id = self.env.ref(
            "project_identification.time_tracking_type"
        )
        project_data = {
            # name is not required for a production order
            "name": data.get("name", "/"),
            "partner_id": data.get("partner_id", False),
            "type_id": time_tracking_type_id.id,
        }
        if "sale_order_id" in data:
            sale_order_id = self.env["sale.order"].browse(data.get("sale_order_id"))
            if sale_order_id:
                project_data.update(
                    {
                        "name": sale_order_id.name,
                        # Use the same partner than the sale order. The shipping
                        # partner is retrieved using `project_partner_location`
                        # module and the `partner_shipping_id` field.
                        "partner_id": sale_order_id.partner_id.id,
                    }
                )
        return project_data

    def action_create_project(self):
        for rec in self:
            data = rec.sudo().read(load=False)[0]
            project_id = self._create_or_retrieve_project(data)
            if project_id:
                rec.write(
                    {
                        "project_id": project_id.id,
                        "allow_timesheets": True,
                    }
                )
