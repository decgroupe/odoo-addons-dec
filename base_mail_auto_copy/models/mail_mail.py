# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import models


class MailMail(models.Model):
    _inherit = "mail.mail"

    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        mail_authors = {}
        for rec in self:
            # Use Message-Id as the `mail.mail` record ID will not be
            # available in the `send_email` method from the `ir.mail.server`
            mail_authors[rec.message_id] = rec.author_id.id
        return super(MailMail, self.with_context(mail_authors=mail_authors))._send(
            auto_commit=auto_commit,
            raise_exception=raise_exception,
            smtp_session=smtp_session,
        )
