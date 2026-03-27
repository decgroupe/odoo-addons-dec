# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import api, fields, models


class DocumentPage(models.Model):
    """Extend document.page to compute and display category complete name."""

    _inherit = "document.page"
    _parent_name = "parent_id"
    _parent_store = True
    _order = "complete_name"

    parent_path = fields.Char(index=True)
    complete_name = fields.Char(
        string="Complete Name",
        compute="_compute_complete_name",
        store=True,
        recursive=True,
    )

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        """Compute the full hierarchical name for category pages."""
        for rec in self:
            if rec.parent_id and rec.type == "category":
                rec.complete_name = f"{rec.parent_id.complete_name} / {rec.name}"
            else:
                rec.complete_name = rec.name

    def _compute_display_name(self):
        """Override display name to use complete_name for all document pages."""
        for rec in self:
            rec.display_name = rec.complete_name
