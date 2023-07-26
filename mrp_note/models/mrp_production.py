# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import _, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    note = fields.Text(
        string="Internal Notes",
        tracking=True,
    )
