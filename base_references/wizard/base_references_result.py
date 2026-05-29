# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026


from odoo import fields, models


class BaseReferencesResult(models.TransientModel):
    """Stores one record reference found during the reference search."""

    _name = "base.references.result"
    _description = "Record Reference Search Result"
    _order = "model, res_id, field_name"

    wizard_id = fields.Many2one(
        comodel_name="base.references.wizard",
        string="Wizard",
        required=True,
        ondelete="cascade",
    )
    model = fields.Char(
        string="Model",
        required=True,
    )
    res_id = fields.Integer(
        string="Record ID",
        required=True,
    )
    record_display_name = fields.Char(
        string="Display Name",
    )
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Field",
        ondelete="set null",
    )
    field_name = fields.Char(
        string="Field",
    )
    field_label = fields.Char(
        string="Field Label",
    )
    reference_type = fields.Selection(
        selection=[
            ("many2one", "Many2one"),
            ("many2many", "Many2many"),
            ("reference", "Reference"),
            ("many2one_reference", "Many2one Reference"),
        ],
        string="Reference Type",
    )

    def action_open_record(self):
        """Open the referencing record in a form view."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.record_display_name or self.env._("Record"),
            "res_model": self.model,
            "res_id": self.res_id,
            "view_mode": "form",
            "target": "current",
        }
