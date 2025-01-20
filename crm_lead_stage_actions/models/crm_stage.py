# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CrmStage(models.Model):
    _inherit = "crm.stage"

    is_lost = fields.Boolean("Is Lost Stage?")
