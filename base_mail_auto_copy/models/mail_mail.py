# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import models, api


class MailMail(models.Model):
    _inherit = "mail.mail"

    @api.multi
    def _send(
        self, auto_commit=False, raise_exception=False, smtp_session=None
    ):
        return super(
            MailMail, self.with_context(mail_author_id=self.author_id.id)
        )._send(
            auto_commit=auto_commit,
            raise_exception=raise_exception,
            smtp_session=smtp_session
        )
