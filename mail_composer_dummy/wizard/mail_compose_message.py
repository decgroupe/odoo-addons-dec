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

    def get_mail_values(self, res_ids):
        results = super(MailComposer, self).get_mail_values(res_ids)
        for res_id, mail_values in results.items():
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

    def send_mail(self, auto_commit=False):
        res = super(MailComposer, self).send_mail(auto_commit)
        # Fix warning: The method send_mail of the object mail.compose.message can
        # not return `None` !
        if res is None:
            return True
        else:
            return res
