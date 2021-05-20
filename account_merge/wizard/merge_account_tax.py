# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2021

from odoo import api, fields, models


class MergeAccountTax(models.TransientModel):
    _inherit = "merge.object.wizard"
    _name = "merge.account.tax.wizard"
    _description = "Merge Account Tax Wizard"
    _model_merge = "account.tax"
    _table_merge = "account_tax"

    object_ids = fields.Many2many(_model_merge, string="Account Tax")
    dst_object_id = fields.Many2one(
        _model_merge, string="Destination Account Tax"
    )

    def _merge(self, object_ids, dst_object=None, extra_checks=True):
        return super()._merge(object_ids, dst_object, extra_checks)
