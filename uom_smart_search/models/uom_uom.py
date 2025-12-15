# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2020

from odoo import api, models


class UoM(models.Model):
    _inherit = "uom.uom"
    _name_search_order = "factor DESC, name"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        res = super().name_search(name=name, args=args, operator=operator, limit=limit)
        if not args:
            args = []

        if name:
            records = self.env["uom.uom"]
            positive_operators = ["=", "ilike", "=ilike", "like", "=like"]
            if operator in positive_operators:
                records = self.search_fetch(
                    args + [("name", "=ilike", name)],
                    field_names=[],
                    limit=limit,
                    order=self._name_search_order,
                )
            # bonus searches (step 1)
            if not limit or len(records) < limit:
                bonus_limit = (limit - len(records)) if limit else False
                bonus_records = self.search_fetch(
                    args
                    + [
                        ("name", "=ilike", name + "%"),
                        ("id", "not in", records.ids),
                    ],
                    field_names=[],
                    limit=bonus_limit,
                    order=self._name_search_order,
                )
                records |= bonus_records

            # bonus searches (step 2)
            if not limit or len(records) < limit and operator != "=ilike":
                bonus_limit = (limit - len(records)) if limit else False
                bonus_records = self.search_fetch(
                    args
                    + [
                        ("name", operator, name),
                        ("id", "not in", records.ids),
                    ],
                    field_names=[],
                    limit=bonus_limit,
                    order=self._name_search_order,
                )
                records |= bonus_records

            if records:
                # same code from base implementation of name_search
                return [(record.id, record.display_name) for record in records.sudo()]

        # fallback to super implementation
        return res
