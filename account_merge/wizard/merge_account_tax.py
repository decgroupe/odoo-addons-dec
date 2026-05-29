# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import fields, models


class MergeAccountTax(models.TransientModel):
    _inherit = "merge.object.wizard"
    _name = "merge.account.tax.wizard"
    _description = "Merge Account Tax Wizard"
    _model_merge = "account.tax"
    _table_merge = "account_tax"

    object_ids = fields.Many2many(
        comodel_name=_model_merge,
        string="Account Tax",
    )
    dst_object_id = fields.Many2one(
        comodel_name=_model_merge,
        string="Destination Account Tax",
    )

    def _get_fk_on(self, table):
        """Exclude repartition lines from FK updates to preserve dst tax structure."""
        relations = super()._get_fk_on(table)
        return [(t, c) for t, c in relations if t != "account_tax_repartition_line"]

    def _merge(self, object_ids, dst_object=None, unique_xmlid=False):
        """Merge account taxes with unique xmlid enforcement."""
        return super()._merge(object_ids, dst_object, unique_xmlid=True)
