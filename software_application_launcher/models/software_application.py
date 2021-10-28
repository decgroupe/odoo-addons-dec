# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SoftwareApplication(models.Model):
    _inherit = 'software.application'

    corner_image = fields.Binary(
        "Corner Image",
        attachment=True,
    )
    pictogram_image = fields.Binary(
        "Pictogram Image",
        attachment=True,
    )
    image_ids = fields.One2many(
        'software.application.image',
        'application_id',
        string='Tooltips',
    )
