# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_origin = fields.Char(
        related="move_id.invoice_origin",
        string="Origin",
        help="The document(s) that generated the invoice.",
        store=True,
    )
