# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jun 2021

from odoo import api, fields, models


class MergeTask(models.TransientModel):
    _inherit = "merge.object.wizard"
    _name = "merge.project.task.wizard"
    _description = "Merge Task Wizard"
    _model_merge = "project.task"
    _table_merge = "project_task"

    object_ids = fields.Many2many(_model_merge, string="Task")
    dst_object_id = fields.Many2one(_model_merge, string="Task")

    def _merge(self, object_ids, dst_object=None, extra_checks=True):
        return super()._merge(
            object_ids,
            dst_object.with_context(mail_auto_subscribe_no_notify=True),
            extra_checks
        )
