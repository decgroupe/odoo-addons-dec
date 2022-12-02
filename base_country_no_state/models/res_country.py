# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2021

from odoo import fields, models, api


class ResCountry(models.Model):
    _inherit = "res.country"

    hide_state = fields.Boolean("Hide State")