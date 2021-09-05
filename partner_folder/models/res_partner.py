# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import _, api, models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    folder_uri = fields.Char(string='Folder')
