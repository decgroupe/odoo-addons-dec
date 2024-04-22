# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021


from email.utils import parseaddr

import lxml

from odoo import models, tools
from odoo.tools import pycompat


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_belong_to_us(self, message):
        res = False
        email_from = tools.decode_message_header(message, "From")
        email_from = parseaddr(email_from)[1]
        email_domain = email_from.partition("@")[2]
        catchall_domain_lowered = (
            self.env["ir.config_parameter"].sudo().get_param("mail.catchall.domain", "")
        )
        if catchall_domain_lowered:
            catchall_domain_lowered = catchall_domain_lowered.strip().lower()
        if catchall_domain_lowered:
            catchall_domains = [catchall_domain_lowered]
            catchall_domains_allowed = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("mail.catchall.domain.allowed")
            )
            if catchall_domains_allowed:
                for domain in catchall_domains_allowed.lower().split(","):
                    if domain not in catchall_domains:
                        catchall_domains.append(domain)
            res = email_domain in catchall_domains
        return res

    def _message_parse_process_body_before_sanitize(self, message, body):
        """WARNING: Ensure the commit `[DEC][IMP] mail: Allow parsing before sanitizing`
        is added to your Odoo/OCB runtime
        """
        res = super()._message_parse_process_body_before_sanitize(message, body)
        if res:
            # Only remove signature for an e-mail coming from our domain
            if self._message_belong_to_us(message):
                res = self._remove_gmail_signatures(res)
        return res

    def _remove_gmail_signatures(self, body):
        if not body:
            return body
        try:
            root = lxml.html.fromstring(body)
        except ValueError:
            # In case the email client sent XHTML, fromstring will fail because 'Unicode strings
            # with encoding declaration are not supported'.
            root = lxml.html.fromstring(body.encode("utf-8"))

        postprocessed = False
        to_remove = []
        for node in root.iter():
            # TODO: we should probably remove only the first occurence, so
            # a context var could be used to force remove all

            if "gmail_signature" in (
                node.get("data-smartmails") or ""
            ) or "gmail_signature" in (node.get("class") or ""):
                postprocessed = True
                if node.getparent() is not None:
                    to_remove.append(node)

        for node in to_remove:
            node.getparent().remove(node)
        if postprocessed:
            body = lxml.etree.tostring(root, pretty_print=False, encoding="UTF-8")
            body = pycompat.to_text(body)
        return body
