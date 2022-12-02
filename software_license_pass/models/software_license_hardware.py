# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SoftwareLicenseHardware(models.Model):
    _inherit = 'software.license.hardware'
