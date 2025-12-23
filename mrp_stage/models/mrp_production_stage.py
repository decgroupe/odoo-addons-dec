# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2022

from odoo import api, fields, models


class ProductionStage(models.Model):
    _name = "mrp.production.stage"
    _description = "Production Stage"
    _order = "sequence, id"

    name = fields.Char(
        string="Stage Name",
        required=True,
        translate=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
        help="Unique lowercase string identifier",
    )
    symbol = fields.Char(
        string="Icon",
        translate=False,
    )
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    fold = fields.Boolean(
        string="Folded in Kanban",
        help="This stage is folded in the kanban view when there are no "
        "records in that stage to display.",
    )
    todo = fields.Boolean(
        string="To-do",
        help="This stage is considered to have actions needed",
    )
    activity_type_id = fields.Many2one(
        comodel_name="mail.activity.type",
        string="Activity Type",
    )

    _sql_constraints = [
        ("code_uniq", "unique (code)", "Code must be unique !"),
    ]

    @api.depends("name", "symbol")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for rec in self:
            if rec.symbol:
                name = f"{rec.symbol} {rec.name}"
            else:
                name = rec.name
            rec.display_name = name
        return res
