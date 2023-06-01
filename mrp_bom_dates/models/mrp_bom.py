# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2020

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    date_start = fields.Date(
        string="Valid From",
        copy=False,
    )

    date_stop = fields.Date(
        string="Valid Until",
        copy=False,
    )
