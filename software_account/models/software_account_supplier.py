# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class SoftwareAccountSupplier(models.Model):
    _name = "software.account.supplier"
    _description = "Software Account supplier"
    _order = "id desc"

    name = fields.Text(
        string="Name",
        required=True,
    )
    image = fields.Binary(
        string="Image",
    )
    rules = fields.Text(
        string="Rules",
    )
    account_count = fields.Integer(
        string="Accounts",
        compute="_compute_account_count",
    )

    @api.depends("name")
    def _compute_account_count(self):
        """Compute the number of software accounts linked to this supplier."""
        data = self.env["software.account"].read_group(
            [("supplier_id", "in", self.ids)],
            ["supplier_id"],
            ["supplier_id"],
        )
        counts = {d["supplier_id"][0]: d["supplier_id_count"] for d in data}
        for rec in self:
            rec.account_count = counts.get(rec.id, 0)

    def action_view_accounts(self):
        """Open the list of software accounts linked to this supplier."""
        return {
            "type": "ir.actions.act_window",
            "name": "Accounts",
            "res_model": "software.account",
            "view_mode": "list,form",
            "domain": [("supplier_id", "=", self.id)],
            "context": {"default_supplier_id": self.id},
        }
