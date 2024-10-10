# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

import re
from odoo import _, api, models

SEARCH_SEPARATOR = "→"
EMOJI_COMPANY = "🏢"
EMOJI_CONTACT = "👷"

class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_contact_type_emoji(self):
        self.ensure_one()
        if self.is_company:
            res = EMOJI_COMPANY
        else:
            res = EMOJI_CONTACT
        return res

    def _get_name_location_identification(self):
        self.ensure_one()
        res = []
        if self.zip:
            res.append(self.zip)
        if self.city:
            res.append(self.city)
        return " ".join(res).strip()

    def _get_name_identifications(self):
        self.ensure_one()
        res = [("%s %s") % (self._get_contact_type_emoji(), self.name)]
        # Add city and zip to quickly identify a partner
        location = self._get_name_location_identification()
        if location and not self.env.context.get("idf_no_location"):
            res.append(("(%s)") % (location))
        if self.email and not self.env.context.get("idf_no_email"):
            res.append(("📧 %s") % (self.email,))
        if len(res) > 1:
            res.insert(1, SEARCH_SEPARATOR)
        return res

    def _compute_display_name(self):
        # ensure name_search is disabled when storing display name
        super(ResPartner, self.with_context(name_search=False))._compute_display_name()

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if SEARCH_SEPARATOR in name:
            name = name.partition(SEARCH_SEPARATOR)[0].strip()
        if name.startswith(EMOJI_COMPANY) or name.startswith(EMOJI_CONTACT):
            name = name[1:].strip()
        # WARNING: Odoo overrides `_name_search`
        names = super(ResPartner, self.with_context(name_search=True)).name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        return names

    def name_get(self):
        if self.env.context.get("name_search"):
            return self.name_get_from_search()
        else:
            return super().name_get()

    @api.depends("name")
    def name_get_from_search(self):
        """Custom naming to quickly identify a production order"""
        res = []
        for rec in self:
            identification = " ".join(rec._get_name_identifications())
            name = identification
            res.append((rec.id, name))
        return res
