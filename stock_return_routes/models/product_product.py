# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def update_routes_after_return_to_stock(self, reason):
        """Swap MTO route with MTO+MTS route on product templates returning to stock."""
        # get routes via helpers from another module
        mto_route = self.env["product.template"]._get_mto_route()
        mto_mts_route = self.env["product.template"]._get_mto_mts_route()
        updated_products = self.env["product.product"]
        # change MTO routes to MTO+MTS (directly on the template)
        for product in self.mapped("product_tmpl_id"):
            route_ids = product.route_ids
            if mto_route in route_ids and mto_mts_route not in route_ids:
                route_ids -= mto_route
                route_ids += mto_mts_route
                product.message_post(
                    body=self.env._(
                        "Route <small><b>%s</b></small> replaced with "
                        "route <small><b>%s</b></small> while "
                        "processing %s."
                    )
                    % (mto_route.name, mto_mts_route.name, reason)
                )
                product.route_ids = route_ids
                updated_products += product.product_variant_ids
        return updated_products.ids
