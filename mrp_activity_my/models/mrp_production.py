# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

from odoo import models, api, fields


class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = ['mrp.production', 'mail.activity.my.mixin']
