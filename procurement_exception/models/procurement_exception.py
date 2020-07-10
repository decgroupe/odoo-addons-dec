# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Jul 2020

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class ProcurementException(models.Model):
    _name = 'procurement.exception'
    _description = "Procurement Exception"

    regex_pattern = fields.Char(
        string='RegEx',
        help="Regular Expression used to parse procurement exception message",
        oldname='message_regex'
    )

    user_id = fields.Many2one(
        'res.users',
        string='User',
        ondelete='cascade',
    )

    def match(self, message):
        self.ensure_one()
        matches = re.search(self.regex_pattern, message)
        if matches and matches.group(0):
            return True
        else:
            return False
