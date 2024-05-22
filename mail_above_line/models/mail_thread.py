# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

import logging
import lxml
import re

from odoo import _, api, models
from odoo.tools import pycompat

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, message_type="notification", **kwargs):
        """When an email is fetched the `_message_route_process` will run `message_post`
        on the matching record if a reference if found.
        """
        if "body" in kwargs:
            kwargs["body"] = self._remove_everything_except_above_this_line(
                kwargs["body"]
            )
        return super().message_post(message_type=message_type, **kwargs)

    def _remove_everything_except_above_this_line(self, body):
        if body == "":
            return body
        REGEX_PATTERN = r"\#\#- .* -\#\#"
        PLACEHOLDER = lxml.html.fromstring("<i>##- %s -##</i>" % _("Content Removed"))
        try:
            root = lxml.html.fromstring(body)
        except ValueError:
            # In case the email client sent XHTML, fromstring will fail because 'Unicode strings
            # with encoding declaration are not supported'.
            root = lxml.html.fromstring(body.encode("utf-8"))

        to_replace = []
        for node in root.iter():
            if node.text:
                matches = re.search(REGEX_PATTERN, node.text)
                if matches and matches.group(0):
                    # our text parent node is probably the blockquote
                    if node.getparent() is not None:
                        to_replace.append(node.getparent())

        if to_replace:
            for node in to_replace:
                node.getparent().replace(node, PLACEHOLDER)
            body = lxml.etree.tostring(root, pretty_print=False, encoding="UTF-8")
            body = pycompat.to_text(body)
        return body
