# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import _, api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_contact_type_emoji(self):
        self.ensure_one()
        if self.is_company:
            res = "🏢"
        else:
            res = "👷"
        return res

    def _get_name_location_identification(self):
        self.ensure_one()
        if self.zip or self.city:
            res = ("%s %s") % (self.zip, self.city)
        else:
            res = ""
        return res.strip()

    def _get_name_identifications(self):
        self.ensure_one()
        res = [("%s %s") % (self._get_contact_type_emoji(), self.display_name)]
        # Add city and zip to quickly identify a partner
        location = self._get_name_location_identification()
        if location:
            res.append(("(%s)") % (location))
        if self.email and not self.env.context.get("idf_no_email"):
            res.append(("📧 %s") % (self.email,))
        return res

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        # Make a search with default criteria
        names = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        result = []
        for item in names:
            # Don't reuse item[1] lazy result as it contains line feeds
            # with address
            partner = self.browse(item[0])[0]
            identifications = " ".join(partner._get_name_identifications())
            result.append((item[0], identifications))
        return result
