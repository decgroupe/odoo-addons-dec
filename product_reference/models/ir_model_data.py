# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import _, api, models
from odoo.exceptions import UserError


class IrModelData(models.Model):
    _inherit = "ir.model.data"

    @api.model
    def modelid_to_xmlid(
        self,
        model_name,
        model_id,
        module,
        name,
        noupdate=False,
        replace=False
    ):
        record = self.env[model_name].browse(model_id)
        self.record_to_xmlid(record, module, name, noupdate, replace)
        return True

    @api.model
    def record_to_xmlid(
        self, record, module, name, noupdate=False, replace=False
    ):
        if replace:
            xml_ids = self.sudo().search(
                [
                    ('model', '=', record._name),
                    ('res_id', '=', record.id),
                ]
            )
            xml_ids.unlink()
        else:
            current_xmlid = self.get_xmlid_as_string(record)
            if current_xmlid is not None:
                raise UserError(
                    _("This record already owns an external ID: %s") %
                    (current_xmlid, )
                )
        if module and name:
            self.sudo().create(
                {
                    'module': module,
                    'name': name,
                    'model': record._name,
                    'res_id': record.id,
                    'noupdate': noupdate,
                }
            )
            self._create_parents_xmlid(record, noupdate, replace)
        return True

    @api.model
    def get_xmlid(self, record):
        domain = [('model', '=', record._name), ('res_id', '=', record.id)]
        model_data = self.search(domain, limit=1)
        if model_data:
            return model_data.module, model_data.name
        else:
            return None, None

    @api.model
    def get_xmlid_as_string(self, record):
        module, name = self.get_xmlid(record)
        if module and name:
            return "%s.%s" % (module, name)
        else:
            return None

    @api.model
    def _create_parents_xmlid(self, record, noupdate=False, replace=False):
        module, name = self.get_xmlid(record)
        for parent_model, parent_field in record._inherits.items():
            parent = record[parent_field]
            puffix = name + '_' + parent_model.replace('.', '_')
            self.record_to_xmlid(parent, module, puffix, noupdate, replace)
