# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

from odoo import models, api, fields
import logging

logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    allowed_databases = fields.Char(
        string="Allowed Databases",
        help="Comma-separated list of database names allowed to send "
        "e-mails with this server"
    )
