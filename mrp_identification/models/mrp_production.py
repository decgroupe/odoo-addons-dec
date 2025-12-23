# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import api, models

SEARCH_SEPARATOR = " →"


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        # it is important to clean the name from identification to avoid issues
        # with other modules that would alter the name_search behavior (typefast)
        names = super(MrpProduction, self.with_context(name_search=True)).name_search(
            name=self._clean_name_identification(name),
            args=args,
            operator=operator,
            limit=limit,
        )
        # if returned names are empty, launch a new search on products
        if not names and name and not args and operator == "ilike":
            args = [
                "|",
                ("partner_zip_id", operator, name),
                "|",
                ("bom_id.code", operator, name),
                "|",
                ("product_id.default_code", operator, name),
                ("product_id.name", operator, name),
            ]
            name = ""
            names = super(
                MrpProduction, self.with_context(name_search=True)
            ).name_search(name=name, args=args, operator=operator, limit=limit)
        return names

    @api.depends(
        "name",
        "bom_id",
        "bom_id.product_tmpl_id",
        "partner_id",
        "partner_zip_id",
        "stage_id",
        "stage_id.symbol",
    )
    def _compute_display_name(self):
        """Custom naming to quickly identify a production order"""
        res = super()._compute_display_name()
        if self.env.context.get("name_search"):
            # Custom naming to quickly identify a production order
            for rec in self:
                identification = " ".join(rec._get_name_identifications())
                if identification:
                    name = f"{rec.name}{SEARCH_SEPARATOR} {identification}"
                else:
                    name = rec.name
                # add suport for `mrp_stage`
                if rec.stage_id and rec.stage_id.symbol:
                    name = f"{rec.stage_id.symbol} {name}"
                rec.display_name = name
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
        res = []
        if self.bom_id:
            res.append(f"🔧 {self.bom_id.display_name}")
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
        return res

    def _clean_name_identification(self, name):
        if name and SEARCH_SEPARATOR in name:
            name = name.partition(SEARCH_SEPARATOR)[0]
            # remove possible symbol from stage name
            if name and not name[0].isalpha():
                # we cannot rely on the length of the symbol because it can be 1 or
                # more characters (invisible for variation). Instead we partition the
                # string to remove the symbol
                name = name.partition(" ")[2]
        return name
