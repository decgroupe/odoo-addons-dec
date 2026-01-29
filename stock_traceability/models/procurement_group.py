# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    def get_head_desc(self):
        return f"📋{self.sudo().name}", ""
