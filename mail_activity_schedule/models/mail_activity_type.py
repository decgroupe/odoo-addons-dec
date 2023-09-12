# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2022

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class MailActivityType(models.Model):
    _inherit = "mail.activity.type"

    plannable = fields.Boolean(
        string="Plannable",
        help="If set, activities of this type will be plannable with a start "
        "and end date",
    )
