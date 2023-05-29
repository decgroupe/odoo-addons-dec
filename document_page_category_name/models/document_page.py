# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import api, fields, models


class DocumentPage(models.Model):
    _inherit = "document.page"
    _parent_name = "parent_id"
    _parent_store = True
    _order = "complete_name"

    parent_path = fields.Char(index=True)
    complete_name = fields.Char(
        string="Complete Name",
        compute="_compute_complete_name",
        store=True,
    )

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id and rec.type == "category":
                rec.complete_name = "%s / %s" % (
                    rec.parent_id.complete_name,
                    rec.name,
                )
            else:
                rec.complete_name = rec.name

    @api.depends("name", "complete_name", "type")
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.complete_name))
        return result
