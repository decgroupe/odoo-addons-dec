# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models
from odoo.exceptions import UserError

AUTO_INC_CHAR = "#"


class RefReferenceLine(models.Model):
    """Description"""

    _name = "ref.reference.line"
    _description = "Reference line"
    _rec_name = "value"
    _order = "sequence"

    reference_id = fields.Many2one(
        comodel_name="ref.reference",
        string="Reference",
        required=True,
        ondelete="cascade",
    )
    property_id = fields.Many2one(
        comodel_name="ref.property",
        string="Property",
        required=True,
    )
    attribute_id = fields.Many2one(
        comodel_name="ref.attribute",
        string="Attribute",
    )
    value = fields.Char(
        string="Value",
    )
    sequence = fields.Integer(
        string="Position",
        required=True,
    )
    property_fixed = fields.Boolean(
        related="property_id.fixed",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_id = self.env["ref.property"].browse(vals.get("property_id"))
            if property_id.fixed:
                if not vals.get("attribute_id"):
                    raise UserError(
                        self.env._(
                            "Missing attribute for property %(num)d : %(name)s",
                            num=vals.get("sequence", 0),
                            name=property_id.name,
                        )
                    )
            else:
                if not vals.get("value"):
                    raise UserError(
                        self.env._(
                            "Missing value for property %(num)d : %(name)s",
                            num=vals.get("sequence", 0),
                            name=property_id.name,
                        )
                    )
        line_ids = super().create(vals_list)
        return line_ids

    @api.onchange("value")
    def onchange_value(self):
        self.ensure_one()
        if not self.property_fixed:
            self.value = self.property_id.validate_value(self.value)
