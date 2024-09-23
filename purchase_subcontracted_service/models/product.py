# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    property_subcontracted_service = fields.Boolean(
        compute="_compute_property_subcontracted_service",
        inverse="_inverse_property_subcontracted_service",
        # override this attribute otherwise it is not possible to override this
        # field because a `company_dependent` field is internally computed using:
        # - _default_company_dependent
        # - _compute_company_dependent
        # - _inverse_company_dependent
        # - _search_company_dependent
        company_dependent=False,
    )

    @api.depends("service_to_purchase")
    def _compute_property_subcontracted_service(self):
        """Re-use built-in `service_to_purchase` field used to directly puchase
        products from sale order"""
        for rec in self:
            rec.property_subcontracted_service = rec.service_to_purchase

    def _inverse_property_subcontracted_service(self):
        for rec in self:
            rec.service_to_purchase = rec.property_subcontracted_service
