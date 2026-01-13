# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

import logging
import re

import lxml

from odoo import api, models
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
        PLACEHOLDER = lxml.html.fromstring(
            "<i>##- %s -##</i>" % self.env._("Content Removed")  # noqa: UP031
        )
        # pattern used to detect a forwarded message (GMail, Thunderbird)
        FORWARDED_MESSAGE = r"--- Forwarded [Mm]essage ---"
        try:
            root = lxml.html.fromstring(body)
        except ValueError:
            # In case the email client sent XHTML, fromstring will fail because
            # 'Unicode strings with encoding declaration are not supported'.
            root = lxml.html.fromstring(body.encode("utf-8"))

        to_replace = []
        for node in root.iter():
            # create a combination of node.text and node.tail otherwise we could miss
            # data with standalone tags like `br`: <div>TEXT<br>TAIL</div>
            node_text = node.text
            if node.tail:
                if node_text:
                    node_text += node.tail
                else:
                    node_text = node.tail
            if node_text:
                node_text = node_text.replace("\n", "").strip()
            if node_text:
                # if this message appears to be forwarded then stop replacing
                # message next content
                matches = re.search(FORWARDED_MESSAGE, node_text)
                if matches and matches.group(0):
                    break
                matches = re.search(REGEX_PATTERN, node_text)
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
