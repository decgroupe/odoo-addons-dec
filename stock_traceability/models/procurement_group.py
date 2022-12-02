# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import models, api, fields


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    def get_head_desc(self):
        g = self.sudo()
        head = '🧩{0}'.format(g.name)
        if g.sale_id and g.sale_id.name != g.name:
            desc = g.sale_id.name
        else:
            desc = ''
        return head, desc
