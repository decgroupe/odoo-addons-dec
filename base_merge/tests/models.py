# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo import api, fields, models


class MergeTestTag(models.Model):
    """Fake tag model used to test many2many field merge behavior."""

    _name = "merge.test.tag"
    _description = "Merge Test Tag"

    name = fields.Char(required=True)


class MergeTestModel(models.Model):
    """Fake model used as merge target in base_merge tests."""

    _name = "merge.test.model"
    _description = "Merge Test Model"
    _parent_name = "parent_id"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    amount = fields.Integer(default=0)
    amount_float = fields.Float(default=0.0)
    date_field = fields.Date()
    datetime_field = fields.Datetime()
    state = fields.Selection(
        selection=[("draft", "Draft"), ("done", "Done")],
        default="draft",
    )
    description = fields.Text()
    note = fields.Html()
    name_upper = fields.Char(
        compute="_compute_name_upper",
        store=True,
        readonly=True,
        compute_sudo=True,
    )
    parent_id = fields.Many2one(comodel_name="merge.test.model")
    child_ids = fields.One2many(
        comodel_name="merge.test.model",
        inverse_name="parent_id",
    )
    tag_ids = fields.Many2many(comodel_name="merge.test.tag")

    @api.depends("name")
    def _compute_name_upper(self):
        """Compute an uppercase copy of name, used to test stored computed fields."""
        for record in self:
            record.name_upper = (record.name or "").upper()


class MergeTestHolder(models.Model):
    """Fake model holding relational links to the merge target."""

    _name = "merge.test.holder"
    _description = "Merge Test Holder"

    name = fields.Char(required=True)
    merge_id = fields.Many2one(comodel_name="merge.test.model", required=True)
    ref = fields.Reference(selection=[("merge.test.model", "Merge Test Model")])


class MergeTestWizard(models.TransientModel):
    """Fake merge wizard for merge.test.model."""

    _inherit = "merge.object.wizard"
    _name = "merge.test.model.wizard"
    _description = "Merge Test Model Wizard"

    _model_merge = "merge.test.model"
    _table_merge = "merge_test_model"
    object_ids = fields.Many2many(comodel_name="merge.test.model", string="Objects")
    dst_object_id = fields.Many2one(
        comodel_name="merge.test.model",
        string="Destination Object",
    )

    def _get_summable_fields(self):
        """Return fields summed on destination record during merge."""
        return ["amount", "amount_float"]
