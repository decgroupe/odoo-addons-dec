# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2022

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MailActivityType(models.Model):
    _inherit = "mail.activity.type"
