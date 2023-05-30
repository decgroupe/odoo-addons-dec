# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import models, fields


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    calendar_name = fields.Char(
        string="Meeting Name",
        help="If set, a custom name that will be used when creating the "
        "meeting instead of the default name",
    )
