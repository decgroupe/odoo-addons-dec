# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import api, models

SEARCH_SEPARATOR = " →"


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        # Make a search with default criteria
        names = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        # Add more details to quickly identify a ticket
        result = []
        for item in names:
            rec = self.browse(item[0])[0]
            rec = rec.with_context(idf_include_name_search=True)
            identification = " ".join(rec._get_name_identifications())
            result.append((item[0], identification))
        return result

    @api.depends("team_id", "stage_id")
    def _get_name_identifications(self):
        self.ensure_one()
        res = []
        if self.team_id:
            res.append(self.team_id.name)
        if self.partner_id:
            res.append(
                "%s %s"
                % (
                    self.partner_id._get_contact_type_emoji(),
                    self.partner_id.display_name,
                )
            )
        if self.partner_zip_id:
            res.append("🗺️ %s" % (self.partner_zip_id.display_name))
        if self.env.context.get("idf_include_name_search"):
            name = self.display_name
            if res:
                res.insert(0, "%s%s" % (name, SEARCH_SEPARATOR))
            else:
                res.insert(0, name)
        if self.stage_id and not self.stage_id.name[0].isalpha():
            emoji = self.stage_id.name[0]
            res.insert(0, emoji)
        return res
