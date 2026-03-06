# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022

import logging
from binascii import Error as binascii_error

from odoo import tools
from odoo.tools.misc import clean_context

from odoo.addons.mail.models.mail_message import _image_dataurl

_logger = logging.getLogger(__name__)


# Reuse logic from `odoo/addons/mail/models/mail_message.py:Message.create`
def convert_images_to_attachments(record, field_name):
    # pylint: disable=W8121
    Attachments = record.env["ir.attachment"].with_context(
        clean_context(record._context)
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
                        "res_model": record._name,
                        "res_id": record.id,
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
                att.append((4, att.id))
                data_to_url[key] = [
                    f"/web/image/{att.id}?access_token={att.access_token}",
                    name,
                ]
        return f'{data_to_url[key][0]}{match.group(3)} alt="{data_to_url[key][1]}"'

    record.write(
        {
            field_name: _image_dataurl.sub(
                base64_to_boundary, tools.ustr(record[field_name])
            ),
        }
    )
