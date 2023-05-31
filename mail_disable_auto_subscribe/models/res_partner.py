# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    auto_subscribe_on_tag = fields.Boolean(
        string="Auto subscribe on tag",
        default=True,
        help="If checked, will be automatically added as a follower "
        "of any model with chatter support when tagged in "
        "the chat. (only in models which add `mail_post_autofollow=True` "
        "to the context in `message_post()`",
    )
    auto_subscribe_on_message = fields.Boolean(
        string="Auto subscribe on message",
        default=True,
        help="If checked, will be automatically added as a follower "
        "of any model with chatter support when a new message is posted or "
        "answered in the chat.",
    )
    auto_subscribe_on_activity = fields.Boolean(
        string="Auto subscribe on activity",
        default=True,
        help="If checked, will be automatically added as a follower "
        "of any model with activity support when an activity is assigned "
        "to you.",
    )
