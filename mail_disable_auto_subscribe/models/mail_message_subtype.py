# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022

import logging

from odoo import tools, fields, models, _

_logger = logging.getLogger(__name__)


class MailMessageSubtype(models.Model):
    _inherit = 'mail.message.subtype'

    excluded_res_model_ids = fields.Many2many(
        comodel_name='ir.model',
        string='Excluded models',
        help="This subtype will not be included as default for models "
        "in this list.",
        domain="[('transient', '=', False)]",
    )

    @tools.ormcache('self.env.uid', 'model_name')
    def _default_subtypes(self, model_name):
        subtype_ids, internal_ids, external_ids = super(
        )._default_subtypes(model_name)

        if model_name:
            domain = [('excluded_res_model_ids.model', '=', model_name)]
            excluded_ids = self.search(domain)
            if excluded_ids.ids:
                subtype_ids = [
                    x for x in subtype_ids if x not in excluded_ids.ids
                ]
                internal_ids = [
                    x for x in internal_ids if x not in excluded_ids.ids
                ]
                external_ids = [
                    x for x in external_ids if x not in excluded_ids.ids
                ]

        return subtype_ids, internal_ids, external_ids
