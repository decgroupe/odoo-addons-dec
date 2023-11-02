# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023
import logging

from odoo import api, fields, models
_logger = logging.getLogger(__name__)


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"
    _order = "sequence, id"

    sequence = fields.Integer(
        default=100,
        help="The type with the smallest sequence is the default value in leave request",
    )

    @api.model
    def _model_sorting_key(self, leave_type):
        res = (-leave_type.sequence,) + super()._model_sorting_key(leave_type)
        _logger.debug("%s > %s", leave_type.name, res)
        return res
