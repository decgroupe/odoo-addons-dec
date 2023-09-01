# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_done(self):
        for picking in self.filtered(
            lambda p: p.state not in ["draft", "done", "cancel"]
        ):
            picking._action_done()
