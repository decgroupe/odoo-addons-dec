# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2021

from odoo import models


class SoftwareLicenseHardware(models.Model):
    _inherit = 'software.license.hardware'
