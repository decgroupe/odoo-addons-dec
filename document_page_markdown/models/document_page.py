# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

import re
import string

from odoo import models, fields, api


class DocumentPage(models.Model):
    _inherit = 'document.page'

    content_markdown = fields.Text(
        string="Content",
        # compute="_compute_content",
        # inverse="_inverse_content",
        # search="_search_content",
        # required=True,
        copy=True,
    )

    def write(self, vals):
        res = super(DocumentPage, self).write(vals)
        if res:
            for rec in self.filtered(lambda x: x.type == "content"):
                if rec.content_markdown != rec.history_head.content_markdown:
                    rec._create_history(
                        {
                            "name": vals.get('draft_name') or rec.draft_name,
                            "summary": rec.draft_summary,
                            "content": rec.content,
                            "content_markdown": rec.content_markdown,
                        }
                    )
        return res

    def _create_history(self, vals):
        self.ensure_one()
        if 'content_markdown' not in vals:
            vals['content_markdown'] = self.content_markdown
        return super()._create_history(vals)
