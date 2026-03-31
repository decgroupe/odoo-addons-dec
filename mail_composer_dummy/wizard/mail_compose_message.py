# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2023

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    email_to = fields.Text(
        string="To",
        help="Message recipients (emails)",
    )
    email_cc = fields.Char(
        string="Cc",
        help="Carbon copy message recipients",
    )

    def _prepare_mail_values(self, res_ids):
        """Override to inject custom email_to and email_cc into each mail value dict."""
        results = super()._prepare_mail_values(res_ids)
        for _res_id, mail_values in results.items():
            if self.email_to:
                if "email_to" in mail_values:
                    _logger.info(
                        "Overriding 'email_to' from %s to %s",
                        mail_values["email_to"],
                        self.email_to,
                    )
                mail_values["email_to"] = self.email_to
            if self.email_cc:
                if "email_cc" in mail_values:
                    _logger.info(
                        "Overriding 'email_cc' from %s to %s",
                        mail_values["email_cc"],
                        self.email_cc,
                    )
                mail_values["email_cc"] = self.email_cc
        return results
