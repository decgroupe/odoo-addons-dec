# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022

import logging
from binascii import Error as binascii_error

from odoo import models, tools, api, _
from odoo.addons.mail.models.mail_message import _image_dataurl

_logger = logging.getLogger(__name__)


class DocumentPage(models.Model):
    _inherit = 'document.page'

    # Reuse logic from `odoo/addons/mail/models/mail_message.py:Message.create`
    def _convert_content_images_to_attachments(self):
        Attachments = self.env['ir.attachment']
        data_to_url = {}
        attachment_ids = []

        def base64_to_boundary(match):
            key = match.group(2)
            if not data_to_url.get(key):
                name = match.group(4) if match.group(
                    4
                ) else 'image%s' % len(data_to_url)
                try:
                    attachment = Attachments.create(
                        {
                            'name': name,
                            'datas': match.group(2),
                            'datas_fname': name,
                            'res_model': self._name,
                            'res_id': self.id,
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
                    attachment.generate_access_token()
                    attachment_ids.append((4, attachment.id))
                    data_to_url[key] = [
                        '/web/image/%s?access_token=%s' %
                        (attachment.id, attachment.access_token), name
                    ]
            return '%s%s alt="%s"' % (
                data_to_url[key][0], match.group(3), data_to_url[key][1]
            )

        self.write(
            {
                "content":
                    _image_dataurl.sub(
                        base64_to_boundary, tools.ustr(self.content)
                    ),
                "attachment_ids":
                    attachment_ids,
            }
        )

    def action_convert_content_images_to_attachments(self):
        self._convert_content_images_to_attachments()
