# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2021

import logging

from odoo import api, models, _

_logger = logging.getLogger(__name__)


class MailMessage(models.AbstractModel):
    _inherit = 'mail.message'

