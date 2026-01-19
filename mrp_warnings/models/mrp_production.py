# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020

from odoo import api, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model_create_multi
    def create(self, vals_list):
        record_ids = super().create(vals_list)
        for rec, vals in zip(record_ids, vals_list, strict=True):
            if vals.get("bom_id"):
                rec._check_bom_warnings(rec.bom_id)
        return record_ids

    def write(self, vals):
        res = super().write(vals)
        if res and ("bom_id" in vals or "state" in vals):
            for rec in self:
                rec._check_bom_warnings(rec.bom_id)
        return res

    @api.model
    def _check_bom_warnings(self, bom_id):
        errors = []
        for line in bom_id.bom_line_ids:
            errors += self._check_bom_line_product(line.product_id)
        if errors:
            errors = ["\n"] + errors
            raise UserError(
                self.env._(
                    "Cannot manufacture product %(product_name)s, because of "
                    "following error(s):"
                    "%(errors)s",
                    product_name=bom_id.product_id.display_name,
                    errors="\n - ".join(errors),
                )
            )

    @api.model
    def _check_bom_line_product(self, product_id):
        res = []
        if not product_id.active:
            res.append(
                self.env._(
                    "%(product_name)s is archived",
                    product_name=product_id.display_name,
                )
            )
        if product_id.state == "obsolete":
            res.append(
                self.env._(
                    "%(product_name)s is obsolete",
                    product_name=product_id.display_name,
                )
            )
        return res
