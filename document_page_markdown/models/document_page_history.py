# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import api, fields, models


class DocumentPageHistory(models.Model):
    _inherit = "document.page.history"

    content_markdown = fields.Text()
