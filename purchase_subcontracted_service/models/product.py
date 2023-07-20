# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    property_subcontracted_service = fields.Boolean(
        compute="_compute_property_subcontracted_service",
    )

    @api.depends("service_to_purchase")
    def _compute_property_subcontracted_service(self):
        for rec in self:
            rec.property_subcontracted_service = rec.service_to_purchase
