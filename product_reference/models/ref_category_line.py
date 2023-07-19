# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class RefCategoryLine(models.Model):
    _name = "ref.category.line"
    _description = "Category line"
    _rec_name = "description"
    _order = "sequence"

    category_id = fields.Many2one(
        comodel_name="ref.category",
        string="Category",
        required=True,
        ondelete="cascade",
    )
    property_id = fields.Many2one(
        comodel_name="ref.property",
        string="Property",
        required=True,
        ondelete="cascade",
    )
    description = fields.Char(
        string="Property description",
        size=128,
    )
    sequence = fields.Integer(
        string="Position",
        required=True,
        default=1,
    )

    _sql_constraints = [
        ("cat_seq_uniq", "unique(category_id, sequence)", "Position must be unique !"),
    ]
