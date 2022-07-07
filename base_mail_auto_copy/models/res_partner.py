# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

import logging

from odoo import fields, models, api, tools

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    copy_sent_email = fields.Boolean(
        string='Receive a copy of all my e-mails',
        default=False,
        help="If checked, will receive a copy of all sent e-mails",
    )
