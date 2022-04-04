# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2022

from odoo import models, api, fields

import logging

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    duration = fields.Integer('Duration', )
    date_start = fields.Datetime(
        string='Start Date',
        help="Default start date for this Activity.",
    )
    date_stop = fields.Datetime(
        string='End Date',
        help="Default end date for this Activity.",
    )
    activity_plannable = fields.Boolean(
        related='activity_type_id.plannable',
        readonly=True,
    )
