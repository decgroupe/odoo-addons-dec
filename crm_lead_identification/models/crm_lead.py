# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

SEARCH_SEPARATOR = "→"


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        # it is important to clean the name from identification to avoid issues
        # with other modules that would alter the name_search behavior (typefast)
        names = super(CrmLead, self.with_context(name_search=True)).name_search(
            name=self._clean_name_identification(name),
            args=args,
            operator=operator,
            limit=limit,
        )
        return names

    def _compute_display_name(self):
        res = super()._compute_display_name()
        if self.env.context.get("name_search"):
            # Custom naming to quickly identify a lead
            for rec in self:
                rec.display_name = " ".join(rec._get_name_identifications())
        return res

    def _search_display_name(self, operator, value):
        if self.env.context.get("name_search"):
            # this steps is only a fallback in case of a direct call, the real cleaning
            # is done in name_search, but we want to be sure that the search is clean
            # in any case
            value = self._clean_name_identification(value)
        res = super()._search_display_name(operator, value)
        return res

    def _get_name_identifications(self):
        self.ensure_one()
        res = [f"[{self.number}] {self.name}"]
        if self.partner_id:
            # contact symbol already added in partner display_name
            self.partner_id.invalidate_model(["display_name"])
            res.append(
                self.partner_id.with_context(
                    idf_no_email=True,
                    idf_no_location=True,
                ).display_name
            )
        if self.partner_zip_id:
            res.append(f"🗺️ {self.partner_zip_id.display_name}")
        if len(res) > 1:
            res.insert(1, SEARCH_SEPARATOR)
        if self.stage_id and not self.stage_id.name[0].isalpha():
            symbol = self.stage_id.name[0]
            res.insert(0, symbol)
        return res

    def _clean_name_identification(self, name):
        if name and SEARCH_SEPARATOR in name:
            name = name.partition(SEARCH_SEPARATOR)[0]
        # remove possible symbol from stage name
        if name and not name[0].isalpha() and name[0] not in ("[", "]"):
            name = name[1:].strip()
        return name

    @api.depends("partner_zip_id", "partner_zip_id.name")
    def _compute_names(self):
        res = super()._compute_names()
        for rec in self:
            if rec.partner_zip_id:
                rec.search_name = f"{rec.search_name} {rec.partner_zip_id.display_name}"
        return res
