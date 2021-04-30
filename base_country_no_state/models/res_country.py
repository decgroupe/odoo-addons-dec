# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Apr 2021

from odoo import fields, models, api


class ResCountry(models.Model):
    _inherit = "res.country"

    hide_state = fields.Boolean("Hide State")