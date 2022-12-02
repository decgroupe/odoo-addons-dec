# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2022

from odoo import api, models, fields


class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'

    holiday_status_id = fields.Many2one(
        domain=[
            '|',
            ('valid', '=', True),
            ('requestable_from_valid', '=', True),
        ],
    )
