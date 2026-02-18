# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024

from odoo import models


class MailActivityMixin(models.AbstractModel):
    _inherit = "mail.activity.mixin"
