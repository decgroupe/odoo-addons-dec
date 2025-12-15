# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2022

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = "crm.lead"
    _rec_names_search = ["search_name"]

    number = fields.Char(
        string="Opportunity Number",
        default="/",
        readonly=True,
        copy=False,
    )
    complete_name = fields.Char(
        string="Complete Name",
        compute="_compute_names",
        store=True,
    )
    search_name = fields.Char(
        string="Search Name",
        compute="_compute_names",
        store=True,
    )

    def _prepare_number(self, values=None):
        seq = self.env["ir.sequence"]
        if values and "company_id" in values:
            seq = seq.with_company(values["company_id"])
        return seq.next_by_code("crm.lead.sequence") or "/"

    def _init_number(self, vals=None):
        if self.type == "opportunity":
            if self.number == "/":
                self.number = self._prepare_number(vals)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec, vals in zip(records, vals_list, strict=True):
            rec._init_number(vals)
        return records

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec._init_number(vals)
        return res

    @api.depends("name", "number", "email_from", "partner_id", "partner_id.name")
    def _compute_names(self):
        for rec in self:
            rec.complete_name = f"[{rec.number}] {rec.name}"
            rec.search_name = rec.complete_name
            if rec.email_from:
                rec.search_name = f"{rec.search_name} {rec.email_from}"
            if rec.partner_id:
                rec.search_name = f"{rec.search_name} {rec.partner_id.display_name}"

    def _compute_display_name(self):
        res = super()._compute_display_name()
        for rec in self:
            rec.display_name = rec.complete_name
        return res

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        # Search over `_rec_names_search` fields
        result = super(CrmLead, self.with_context(name_search=True)).name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        return result
