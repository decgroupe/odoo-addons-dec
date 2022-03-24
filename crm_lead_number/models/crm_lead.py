# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2022

import logging

from odoo import fields, api, models

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    number = fields.Char(
        string='Opportunity Number',
        default="/",
        readonly=True,
    )

    def _prepare_number(self, values=None):
        seq = self.env["ir.sequence"]
        if values and "company_id" in values:
            seq = seq.with_context(force_company=values["company_id"])
        return seq.next_by_code("crm.lead.sequence") or "/"

    def _init_number(self, vals=None):
        if self.type == 'opportunity':
            if self.number == '/':
                self.number = self._prepare_number(vals)

    def create(self, vals):
        record = super().create(vals)
        record._init_number(vals)
        return record

    def write(self, vals):
        res = super().write(vals)
        self._init_number(vals)
        return res
