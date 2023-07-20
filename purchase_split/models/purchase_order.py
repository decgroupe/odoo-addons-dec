# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_split(self):
        pass
