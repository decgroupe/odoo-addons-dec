# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import _, api, models

SEARCH_SEPARATOR = " →"


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if SEARCH_SEPARATOR in name:
            name = name.partition(SEARCH_SEPARATOR)[0]
            # remove 'stage' emoji
            if name and not name[0].isalpha():
                # we cannot rely on the length of the emoji because it can be 1 or
                # more characters (invisible for variation). Instead we partition the
                # string to remove the emoji
                name = name.partition(" ")[2]
        names = super(MrpProduction, self.with_context(name_search=True)).name_search(
            name=name, args=args, operator=operator, limit=limit
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
            names = super(MrpProduction, self.with_context(name_search=True)).name_search(
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
            if identification:
                name = "%s%s %s" % (rec.name, SEARCH_SEPARATOR, identification)
            else:
                name = rec.name
            # add suport for `mrp_stage`
            if rec.stage_id and rec.stage_id.emoji:
                name = "%s %s" % (rec.stage_id.emoji, name)
            res.append((rec.id, name))
        return res

    @api.depends("bom_id", "partner_id", "partner_zip_id")
    def _get_name_identifications(self):
        self.ensure_one()
        res = []
        if self.bom_id:
            res.append("🔧 %s" % (self.bom_id.display_name))
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
        return res
