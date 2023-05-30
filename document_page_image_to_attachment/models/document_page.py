# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022

from odoo import models
from odoo.addons.tools_miscellaneous.tools.base64 import convert_images_to_attachments


class DocumentPage(models.Model):
    _inherit = "document.page"

    def action_convert_content_images_to_attachments(self):
        convert_images_to_attachments(self, "content")
