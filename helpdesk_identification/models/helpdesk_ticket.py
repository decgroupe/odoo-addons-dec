# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import api, fields, models

SEARCH_SEPARATOR = "→"


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @property
    def _rec_names_search(self):
        return list(set(super()._rec_names_search + ["complete_name"]))

    complete_name = fields.Char(
        string="Complete Name",
        compute="_compute_names",
        store=True,
    )

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        # it is important to clean the name from identification to avoid issues
        # with other modules that would alter the name_search behavior (typefast)
        names = super(HelpdeskTicket, self.with_context(name_search=True)).name_search(
            name=self._clean_name_identification(name),
            args=args,
            operator=operator,
            limit=limit,
        )
        return names

    @api.depends("name", "number")
    def _compute_names(self):
        # Custom naming to quickly identify a ticket
        for rec in self:
            rec.complete_name = f"[{rec.number}] {rec.name}"

    @api.depends("complete_name")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        if self.env.context.get("name_search"):
            # Custom naming to quickly identify a lead
            for rec in self:
                rec.display_name = " ".join(
                    rec._get_name_identifications(rec.complete_name)
                )
        else:
            for rec in self:
                rec.display_name = rec.complete_name
        return res

    def _search_display_name(self, operator, value):
        if self.env.context.get("name_search"):
            # this steps is only a fallback in case of a direct call, the real cleaning
            # is done in name_search, but we want to be sure that the search is clean
            # in any case
            value = self._clean_name_identification(value)
        res = super()._search_display_name(operator, value)
        return res

    @api.depends("team_id", "stage_id")
    def _get_name_identifications(self, base_name=None):
        self.ensure_one()
        res = [base_name or self.display_name]
        if self.team_id:
            res.append(self.team_id.name)
        if self.partner_id:
            # contact symbol already added in partner display_name
            self.partner_id.invalidate_model(["display_name"])
            context = self.env.context.copy()
            if "idf_no_email" not in context:
                context["idf_no_email"] = False
            if "idf_no_location" not in context:
                context["idf_no_location"] = False
            res.append(self.partner_id.with_context(**context).display_name)
        # do not add `partner_zip_id` since it is already added in partner display_name
        if len(res) > 1:
            res.insert(1, SEARCH_SEPARATOR)
        if self.stage_id and not self.stage_id.name[0].isalpha():
            symbol = self.stage_id.name[0]
            res.insert(0, symbol)
        return res

    def _clean_name_identification(self, name):
        if name and SEARCH_SEPARATOR in name:
            name = name.partition(SEARCH_SEPARATOR)[0].strip()
        # remove possible symbol from stage name
        if name and not name[0].isalpha() and name[0] not in ("[", "]"):
            name = name[1:].strip()
        return name
