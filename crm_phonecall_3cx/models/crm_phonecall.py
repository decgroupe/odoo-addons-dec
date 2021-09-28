# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

from odoo import api, fields, models


class CrmPhonecall(models.Model):
    _inherit = "crm.phonecall"
