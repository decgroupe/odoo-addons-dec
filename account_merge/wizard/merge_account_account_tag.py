# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import api, fields, models


class MergeAccountAccountTag(models.TransientModel):
    _inherit = "merge.object.wizard"
    _name = "merge.account.account.tag.wizard"
    _description = "Merge Account Tag Wizard"
    _model_merge = "account.account.tag"
    _table_merge = "account_account_tag"

    object_ids = fields.Many2many(_model_merge, string="Account Tag")
    dst_object_id = fields.Many2one(
        _model_merge, string="Destination Account Tag"
    )

    def _merge(self, object_ids, dst_object=None, extra_checks=True):
        return super()._merge(object_ids, dst_object, extra_checks)
