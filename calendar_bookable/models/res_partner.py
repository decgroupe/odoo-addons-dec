# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2023

import logging

from odoo import fields, models, api, tools

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    bookable = fields.Boolean(
        string="Bookable",
        default=False,
        help="If checked, the calendar will consider this partner as a bookable resource",
    )
