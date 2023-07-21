# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    service_tracking = fields.Selection(
        selection_add=[
            ("create_application_pass", "Create an application pass"),
        ],
        ondelete={"block_confirm": "set default"},
    )

    @api.onchange("service_tracking")
    def _onchange_service_tracking(self):
        """Reset project when using this setting."""
        res = super()._onchange_service_tracking()
        if self.service_tracking != "create_application_pass":
            self.license_pack_id = False
        return res
