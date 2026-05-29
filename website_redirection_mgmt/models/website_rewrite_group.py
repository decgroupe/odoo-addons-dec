# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2025

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WebsiteRewriteGroup(models.Model):
    _name = "website.rewrite.group"
    _description = "Website Rewrite Group"

    name = fields.Char(
        string="Name",
        required=True,
        help="This is the name of the group",
    )
    note = fields.Text(
        string="Note",
        help="This is a note to help you remember the purpose of this group.",
    )
