# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

import logging
import lxml

from email.utils import parseaddr
from odoo import api, models, _, tools
from odoo.tools import pycompat

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_extract_payload(self, message, save_original=False):
        body, attachments = super()._message_extract_payload(
            message, save_original
        )
        if body:
            # Only remove signature for an e-mail coming from our domain
            email_from = tools.decode_smtp_header(
                message.get('from'), quoted=True
            )
            email_from = parseaddr(email_from)[1]
            email_domain = email_from.partition('@')[2]
            catchall_domain = self.env['ir.config_parameter'].with_user(
            ).get_param("mail.catchall.domain")
            if email_domain == catchall_domain:
                body = self._remove_gmail_signatures(body)
        return body, attachments

    def _remove_gmail_signatures(self, body):
        if not body:
            return body
        try:
            root = lxml.html.fromstring(body)
        except ValueError:
            # In case the email client sent XHTML, fromstring will fail because 'Unicode strings
            # with encoding declaration are not supported'.
            root = lxml.html.fromstring(body.encode('utf-8'))

        postprocessed = False
        to_remove = []
        for node in root.iter():
            # TODO: we should probably remove only the first occurence, so
            # a context var could be used to force remove all
            if 'gmail_signature' in (node.get('data-smartmail') or ''):
                postprocessed = True
                if node.getparent() is not None:
                    to_remove.append(node)

        for node in to_remove:
            node.getparent().remove(node)
        if postprocessed:
            body = lxml.etree.tostring(
                root, pretty_print=False, encoding='UTF-8'
            )
            body = pycompat.to_native(body)
        return body
