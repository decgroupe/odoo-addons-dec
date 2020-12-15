# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Dec 2020

from odoo import api, fields, models


class MergeResCityZip(models.TransientModel):
    _inherit = "merge.object.wizard"
    _name = "merge.res.city.zip.wizard"
    _description = "Merge City Zip Wizard"
    _model_merge = "res.city.zip"
    _table_merge = "res_city_zip"

    object_ids = fields.Many2many(_model_merge, string="City/Location")
    dst_object_id = fields.Many2one(
        _model_merge, string="Destination City/Location"
    )

    group_by_city_id = fields.Boolean("City")

    def _merge(self, object_ids, dst_object=None, extra_checks=True):
        return super()._merge(object_ids, dst_object, extra_checks)
