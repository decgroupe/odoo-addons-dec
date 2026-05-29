# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo import _, fields, models
from odoo.exceptions import AccessDenied


class MergeUomUom(models.TransientModel):
    _inherit = "merge.object.wizard"
    _name = "merge.uom.uom.wizard"
    _description = "Merge Unit of Measure Wizard"
    _model_merge = "uom.uom"
    _table_merge = "uom_uom"

    object_ids = fields.Many2many(
        comodel_name=_model_merge,
        string="Unit of Measure",
    )
    dst_object_id = fields.Many2one(
        comodel_name=_model_merge,
        string="Unit of Measure",
    )

    def _merge(self, object_ids, dst_object=None, extra_checks=True):
        if not self.env.user.has_group("uom_merge.res_group_do_merge"):
            raise AccessDenied(
                _(
                    "You don't have the right to merge units of measure. "
                    "Please contact an Administrator."
                )
            )
        return super()._merge(object_ids, dst_object, extra_checks)

    def _delete_source_objects(self, src_objects):
        return super()._delete_source_objects(src_objects.sudo())
