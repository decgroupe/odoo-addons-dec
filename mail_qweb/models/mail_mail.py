# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging

from premailer import Premailer

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailMail(models.AbstractModel):
    _inherit = "mail.mail"

    @api.model
    def create(self, vals):
        rec = super(MailMail, self).create(vals)
        # Module `mail_inline_css` does not transform emails when they are created from
        # `message_post`, that's why we are copying its premailer functions
        rec.body_html = self._premailer_apply_transform(rec.body_html)
        return rec

    def _premailer_apply_transform(self, html):
        if not html or html and not html.strip():
            return html
        premailer = Premailer(html=html, **self._get_premailer_options())
        return premailer.transform()

    def _get_premailer_options(self):
        return {}
