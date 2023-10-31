# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo import _, fields, models


class ViewCustom(models.Model):
    _inherit = "ir.ui.view.custom"

    create_date = fields.Datetime(index=True)
