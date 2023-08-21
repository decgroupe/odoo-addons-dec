# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2022

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def address_get(self, adr_pref=None):
        res = super().address_get(adr_pref)
        if adr_pref and "delivery" in adr_pref:
            if "default_opportunity_id" in self.env.context:
                opportunity_id = self.env["crm.lead"].browse(
                    self.env.context.get("default_opportunity_id", False)
                )
                if opportunity_id and opportunity_id.partner_shipping_id:
                    res["delivery"] = opportunity_id.partner_shipping_id.id
        return res
