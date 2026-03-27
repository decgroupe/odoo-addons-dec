# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022

import logging
from binascii import Error as binascii_error

from odoo import models
from odoo.tools.misc import clean_context

from odoo.addons.mail.models.mail_message import _image_dataurl

_logger = logging.getLogger(__name__)


class DocumentPage(models.Model):
    _inherit = "document.page"

    def action_convert_content_images_to_attachments(self):
        self._convert_images_to_attachments()

    def _convert_images_to_attachments(self):
        # pylint: disable=W8121
        Attachments = self.env["ir.attachment"].with_context(
            clean_context(self._context)
        )
        data_to_url = {}

        def base64_to_boundary(match):
            key = match.group(2)
            if not data_to_url.get(key):
                name = match.group(4) if match.group(4) else f"image{len(data_to_url)}"
                try:
                    att = Attachments.create(
                        {
                            "name": name,
                            "datas": match.group(2),
                            "res_model": self._name,
                            "res_id": self.id,
                        }
                    )
                except binascii_error:
                    _logger.warning(
                        "Impossible to create an attachment out of badly "
                        "formated base64 embedded image. Image has been "
                        "removed."
                    )
                    # group(3) is the url ending single/double quote
                    # matched by the regexp
                    return match.group(3)
                else:
                    att.generate_access_token()
                    data_to_url[key] = [
                        f"/web/image/{att.id}?access_token={att.access_token}",
                        name,
                    ]
            return f'{data_to_url[key][0]}{match.group(3)} alt="{data_to_url[key][1]}"'

        self.write({"content": _image_dataurl.sub(base64_to_boundary, self.content)})
