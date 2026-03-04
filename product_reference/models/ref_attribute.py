# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020


from odoo import api, fields, models


class RefAttribute(models.Model):
    _name = "ref.attribute"
    _description = "Attribute"
    _rec_name = "name"
    _rec_names_search = ["name", "code"]
    _order = "code"

    property_id = fields.Many2one(
        comodel_name="ref.property",
        string="Property (owner)",
        required=True,
        ondelete="cascade",
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    display_name = fields.Char(
        compute="_compute_display_name",
        store=True,
    )
    auto_inc = fields.Boolean(
        string="Auto-increment",
        default=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        attribute_ids = super().create(vals_list)
        return attribute_ids

    @api.onchange("code")
    def onchange_code(self):
        self.code = self.property_id.validate_value(self.code)

    @api.depends("name", "code")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}"
