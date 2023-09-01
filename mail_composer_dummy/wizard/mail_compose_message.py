# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2023


from odoo import api, fields, models


class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    email_to = fields.Text(
        string="To",
        help="Message recipients (emails)",
    )

    def get_mail_values(self, res_ids):
        results = super(MailComposer, self).get_mail_values(res_ids)
        if self.email_to:
            for res_id, mail_values in results.items():
                if not mail_values.get("email_to"):
                    mail_values["email_to"] = self.email_to
        return results

    def send_mail(self, auto_commit=False):
        res = super(MailComposer, self).send_mail(auto_commit)
        # Fix warning: The method send_mail of the object mail.compose.message can
        # not return `None` !
        if res is None:
            return True
        else:
            return res
