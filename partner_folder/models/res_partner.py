# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    folder_uri = fields.Char(string="Folder")
