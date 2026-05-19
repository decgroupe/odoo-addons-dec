# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo import fields, models


class MailActivityMyTestModel(models.Model):
    """Fake model used in tests for mail_activity_my mixin."""

    _name = "mail.activity.my.test.model"
    _description = "Test Model for Mail Activity My"
    _inherit = ["mail.thread", "mail.activity.mixin", "mail.activity.my.mixin"]

    name = fields.Char()
