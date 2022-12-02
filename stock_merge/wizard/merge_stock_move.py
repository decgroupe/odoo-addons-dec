# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

from odoo import api, fields, models


class MergeStockMove(models.TransientModel):
    _inherit = "merge.object.wizard"
    _name = "merge.stock.move.wizard"
    _description = "Merge Stock Move Wizard"
    _model_merge = "stock.move"
    _table_merge = "stock_move"

    object_ids = fields.Many2many(_model_merge, string="Stock Move")
    dst_object_id = fields.Many2one(_model_merge, string="Stock Move")
    company_id = fields.Many2one(
        'res.company',
        related='dst_object_id.company_id',
        string='Company',
        readonly=True,
        default=lambda self: self.env.user.company_id
    )

    def _merge(self, object_ids, dst_object=None, extra_checks=True):
        return super()._merge(
            object_ids,
            dst_object.with_context(mail_auto_subscribe_no_notify=True),
            extra_checks
        )

    def _log_merge_operation(self, src_objects, dst_object):
        super()._log_merge_operation(src_objects, dst_object)
        # Force state to cancel to allow the `_merge` to `unlink` useless stock
        # moves. We are doing this in `_log_merge_operation` as this is the
        # last method called before unlink
        src_objects.write({'state': 'cancel'})

