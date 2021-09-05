# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import _, api, fields, models


class SoftwareLicenseApplication(models.Model):
    _inherit = 'software.license.application'
