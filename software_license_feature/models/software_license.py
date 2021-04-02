# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

from odoo import api, fields, models


class SoftwareLicense(models.Model):
    _inherit = 'software.license'

    feature_ids = fields.One2many(
        comodel_name='software.license.feature',
        inverse_name='license_id',
        string='Features',
    )

    @api.multi
    def action_sync_features_with_template(self):
        vals_list = []
        for rec in self:
            template_id = rec.application_id.template_id
            for tmpl_feature_id in template_id.feature_ids:
                need_sync = True
                for feature_id in rec.feature_ids:
                    if feature_id.property_id == tmpl_feature_id.property_id:
                        need_sync = False
                if need_sync:
                    vals = tmpl_feature_id._prepare_template_vals()
                    vals['license_id'] = rec.id
                    vals_list.append(vals)
        self.env['software.license.feature'].create(vals_list)

    @api.onchange('application_id')
    def onchange_application_id(self):
        self.ensure_one()
        vals = {}
        feature_ids = []
        self.feature_ids = [(5, )]
        template_feature_ids = self.application_id.template_id.feature_ids
        for template_feature_id in template_feature_ids:
            feature = (
                0, 0, {
                    'sequence': template_feature_id.sequence,
                    'property_id': template_feature_id.property_id.id,
                }
            )
            feature_ids.append(feature)
        vals['feature_ids'] = feature_ids
        self.update(vals)

    @api.multi
    def get_features_dict(self):
        self.ensure_one()
        res = {}
        for feature_id in self.feature_ids:
            if feature_id.customizable:
                value = feature_id.value
            else:
                value = feature_id.value_id.name

            if feature_id.name in res:
                res[feature_id.name].append(value)
            else:
                res[feature_id.name] = [value]

        return res
