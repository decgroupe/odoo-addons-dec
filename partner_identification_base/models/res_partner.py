# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import api, models

SEARCH_SEPARATOR = "→"
SYMBOL_COMPANY = "🏢"
SYMBOL_CONTACT = "👷"


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_contact_type_symbol(self):
        self.ensure_one()
        if self.is_company:
            res = SYMBOL_COMPANY
        else:
            res = SYMBOL_CONTACT
        return res

    def _get_name_location_identification(self):
        self.ensure_one()
        res = []
        if self.zip:
            res.append(self.zip)
        if self.city:
            res.append(self.city)
        return " ".join(res).strip()

    def _get_name_identifications(self, base_name):
        self.ensure_one()
        res = [f"{self._get_contact_type_symbol()} {base_name}"]
        # Add city and zip to quickly identify a partner
        location = self._get_name_location_identification()
        if location and not self.env.context.get("idf_no_location"):
            res.append(f"({location})")
        if self.email and not self.env.context.get("idf_no_email"):
            res.append(f"📧 {self.email}")
        if len(res) > 1:
            res.insert(1, SEARCH_SEPARATOR)
        return res

    def _clean_name_identification(self, name):
        if name and SEARCH_SEPARATOR in name:
            name = name.partition(SEARCH_SEPARATOR)[0].strip()
        if name and (
            name.startswith(SYMBOL_COMPANY) or name.startswith(SYMBOL_CONTACT)
        ):
            name = name[1:].strip()
        return name

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        # it is important to clean the name from identification to avoid issues
        # with other modules that would alter the name_search behavior (typefast)
        names = super(ResPartner, self.with_context(name_search=True)).name_search(
            name=self._clean_name_identification(name),
            args=args,
            operator=operator,
            limit=limit,
        )
        return names

    def _compute_display_name(self):
        res = super()._compute_display_name()
        if self.env.context.get("name_search"):
            for rec in self:
                rec.display_name = " ".join(
                    rec._get_name_identifications(rec.display_name)
                )
        return res

    def _search_display_name(self, operator, value):
        if self.env.context.get("name_search"):
            # this steps is only a fallback in case of a direct call, the real cleaning
            # is done in name_search, but we want to be sure that the search is clean
            # in any case
            value = self._clean_name_identification(value)
        res = super()._search_display_name(operator, value)
        return res
