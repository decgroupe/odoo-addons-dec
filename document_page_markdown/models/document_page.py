# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import fields, models


class DocumentPage(models.Model):
    _inherit = "document.page"

    content_markdown = fields.Text(
        string="Content",
        # compute="_compute_content",
        # inverse="_inverse_content",
        # search="_search_content",
        # required=True,
        copy=True,
    )

    def write(self, vals):
        """Override write to create history when markdown content changes."""
        res = super().write(vals)
        if res:
            for rec in self.filtered(lambda x: x.type == "content"):
                # create a new history when markdown content has changed, also
                # add the html content
                if rec.content_markdown != rec.history_head.content_markdown:
                    rec._create_history(
                        {
                            "page_id": rec.id,
                            "name": rec.draft_name,
                            "summary": rec.draft_summary,
                            "content": rec.content,
                            "content_markdown": rec.content_markdown,
                        }
                    )
        return res

    def _create_history(self, vals):
        """Override to ensure markdown content is always stored in history."""
        self.ensure_one()
        # if markdown content is missing (when recomputing content with
        # `_inverse_content`) always add it
        if "content_markdown" not in vals:
            vals["content_markdown"] = self.content_markdown
        return super()._create_history(vals)
