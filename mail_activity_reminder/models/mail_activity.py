# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024

import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = "mail.activity"
