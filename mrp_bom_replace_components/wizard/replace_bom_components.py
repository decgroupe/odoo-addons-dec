# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ReplaceTuple(models.TransientModel):
    _name = "replace.bom.tuple"
    _description = "Tuple to store product to replace"

    owner_id = fields.Many2one(
        comodel_name="replace.bom.components",
        string="Owner",
        required=True,
        ondelete="cascade",
    )
    previous_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Previous",
        required=True,
    )
    new_product_id = fields.Many2one(
        comodel_name="product.product",
        string="New",
        required=True,
    )


class ReplaceBomComponents(models.TransientModel):
    _name = "replace.bom.components"
    _description = "Replace BoM Components"

    replacement_ids = fields.One2many(
        comodel_name="replace.bom.tuple",
        inverse_name="owner_id",
        string="Replacements",
    )
    bom_ids = fields.Many2many(
        comodel_name="mrp.bom",
        string="Bill of Materials",
        readonly=True,
    )
    bom_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Products",
    )

    @api.model
    def default_get(self, fields):
        """Populate bom_ids and bom_product_ids from the active BoM records."""
        rec = super().default_get(fields)
        active_ids = self._context.get("active_ids")
        active_model = self._context.get("active_model")
        if active_model == "mrp.bom" and active_ids:
            bom_ids = self.env["mrp.bom"].browse(active_ids)
            rec.update(
                {
                    "bom_ids": bom_ids.ids,
                    "bom_product_ids": bom_ids.mapped("bom_line_ids")
                    .mapped("product_id")
                    .ids,
                }
            )
        return rec

    def action_replace(self):
        """Enqueue the replacement job via queue_job."""
        self.with_delay()._do_replace()

    def action_replace_immediately(self):
        """Perform the replacement job immediately."""
        self._do_replace()

    def _do_replace(self):
        """Perform the actual product replacement in the selected BoMs.

        Iterates over all selected BoMs, replaces each component product
        matching the replacement list, and posts a tracking note on each
        modified BoM.
        """
        previous_product_ids = self.replacement_ids.mapped("previous_product_id")
        boms_data = self.env["mrp.bom.line"]._read_group(
            domain=[
                ("product_id", "in", previous_product_ids.ids),
                ("bom_id", "in", self.bom_ids.ids),
            ],
            groupby=["bom_id"],
            aggregates=["__count"],
        )
        for bom, _count in boms_data:
            _logger.info("Processing BoM %s", bom.code)
            values = {"lines": {}}
            replace_count = 0
            for bom_line in bom.bom_line_ids.filtered(
                lambda x: x.product_id in previous_product_ids
            ):
                for replacement_id in self.replacement_ids:
                    if bom_line.product_id == replacement_id.previous_product_id:
                        values["lines"][bom_line] = {
                            "before": bom_line.product_id,
                            "after": replacement_id.new_product_id,
                        }
                        bom_line.product_id = replacement_id.new_product_id
                        replace_count += 1
                        break
            if replace_count > 0:
                bom.message_post_with_source(
                    "mrp_bom_replace_components.track_bom_line_template",
                    render_values=values,
                    subtype_id=self.env.ref("mail.mt_note").id,
                )
