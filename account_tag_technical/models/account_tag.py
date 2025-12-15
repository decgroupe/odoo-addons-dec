# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import api, models


class AccountAccountTag(models.Model):
    _inherit = "account.account.tag"

    @api.depends("name")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        # WARNING: This will also checks for request.session.debug
        if self.env.user.has_group("base.group_no_one"):
            ModelData = self.env["ir.model.data"]
            for rec in self:
                _module, xml_name = ModelData.sudo().get_xmlid(rec)
                if xml_name:
                    rec.display_name = f"{rec.display_name} [{xml_name}]"
        return res
