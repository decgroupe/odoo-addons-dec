# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021


from odoo import api, fields, models


class MailChannel(models.AbstractModel):
    _inherit = "mail.channel"

    subject_prefix = fields.Char(string="Subject's Prefix")

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, message_type="notification", **kwargs):
        if self.subject_prefix:
            if "subject" in kwargs:
                kwargs["subject"] = "%s %s" % (
                    self.subject_prefix,
                    kwargs["subject"],
                )
            else:
                kwargs["subject"] = "%s" % (self.subject_prefix)
        return super().message_post(message_type=message_type, **kwargs)
