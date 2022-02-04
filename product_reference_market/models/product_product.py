# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def get_default_market_bom_products(self):
        """ Return a list of products/services used in the reference price
            computing window (REFManager).
        """
        return self.env['product.product']

    @api.model
    def get_default_market_bom_products_as_ids(self):
        """ Convert list the RPC parsable data
        """
        return [x.id for x in self.get_default_market_bom_products()]

    @api.model
    def get_market_bom_labortime_services(self):
        """ Return a list of services use to compute the labor time """
        return self.env['product.product']

    @api.model
    def get_market_bom_labortime_services_as_ids(self):
        """ Convert list the RPC parsable data
        """
        return [x.id for x in self.get_market_bom_labortime_services()]
