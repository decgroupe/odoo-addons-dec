# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

import logging

from datetime import date, datetime, timedelta

from odoo import api, models

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _inherit = ['helpdesk.ticket', 'mail.activity.my.mixin']
