# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021


from odoo import api, fields, models


class MailChannel(models.AbstractModel):
    _inherit = "mail.channel"

    subject_prefix = fields.Char(string="Subject's Prefix", help="【MAIL】")

    def _remove_subject_client_prefix(self, subject):
        for prefix in ["Re", "RE", "Fw", "FW", "Fwd", "FWD", ":"]:
            if subject.startswith(prefix):
                subject = subject.replace(prefix, "", 1).strip()
        return subject

    def _add_subject_channel_prefix(self, subject):
        if self.subject_prefix:
            if subject:
                if not subject.startswith(self.subject_prefix):
                    subject = "%s %s" % (self.subject_prefix, subject)
            else:
                subject = "%s" % (self.subject_prefix)
        return subject

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, message_type="notification", **kwargs):
        subject = kwargs.get("subject")
        if subject:
            subject = self._remove_subject_client_prefix(subject)
        kwargs["subject"] = self._add_subject_channel_prefix(subject)
        return super().message_post(message_type=message_type, **kwargs)
