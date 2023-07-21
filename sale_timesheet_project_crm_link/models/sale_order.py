# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2022

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_create_project_data(self):
        res = super()._get_create_project_data()
        res.update(
            {
                "linked_lead_id": self.opportunity_id.id,
            }
        )
        return res
