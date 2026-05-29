# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2025

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class WebsiteRewrite(models.Model):
    _inherit = "website.rewrite"

    group_id = fields.Many2one(
        comodel_name="website.rewrite.group",
        string="Grouping",
        help="This is the grouping of the link, e.g. Campaign, Project, etc.",
    )
    content_source_ids = fields.Many2many(
        comodel_name="utm.source",
        relation="website_rewrite_source_rel",
        column1="rewrite_id",
        column2="source_id",
        string="Content Sources",
        help="These are the sources of the link, e.g. Search Engine, another domain, "
        "or name of email list",
    )
    content_target_id = fields.Many2one(
        comodel_name="utm.source",
        string="Content Target",
        help="This is the target of the link, e.g. Image, Video, etc.",
    )
    look = fields.Selection(
        selection=[
            ("clickable_link", "Clickable Link"),
            ("clickable_image", "Clickable Image"),
            ("scannable_qrcode", "Scannable QR Code"),
        ],
        string="Look",
        default=False,
        help="Physical representation of the link",
    )
    tag_ids = fields.Many2many(
        comodel_name="utm.tag",
        relation="website_rewrite_tag_rel",
        column1="rewrite_id",
        column2="tag_id",
        string="Tags",
    )
    note = fields.Html(
        string="Note",
        help="This is a note to help you remember the purpose of this link.",
    )

    @api.onchange("url_from", "url_to")
    def onchange_url(self):
        """Auto-generate name from url_from and url_to when both are set."""
        for rec in self:
            if rec.url_from and rec.url_to:
                # override the name if it is empty or already contains the arrow
                if not rec.name or " 🡢 " in rec.name:
                    name = f"{rec.url_from} 🡢 {rec.url_to}"
                    rec.name = name
