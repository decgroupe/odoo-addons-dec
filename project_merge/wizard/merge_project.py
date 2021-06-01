# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import api, fields, models


class MergeProject(models.TransientModel):
    _inherit = "merge.object.wizard"
    _name = "merge.project.project.wizard"
    _description = "Merge Project Wizard"
    _model_merge = "project.project"
    _table_merge = "project_project"

    object_ids = fields.Many2many(_model_merge, string="Project")
    dst_object_id = fields.Many2one(_model_merge, string="Project")

    def _merge(self, object_ids, dst_object=None, extra_checks=True):
        return super()._merge(
            object_ids,
            dst_object.with_context(mail_auto_subscribe_no_notify=True),
            extra_checks
        )
