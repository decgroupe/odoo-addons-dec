# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

# NOTE: in 18.0, the `channel_email` recipient type no longer exists. the
# recipient classification logic (formerly split between mail.thread and
# mail.channel) is now handled entirely in discuss_channel.py by overriding
# `discuss.channel._notify_get_recipients_groups`. this file is kept for
# historical reference but contains no active overrides.

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"
