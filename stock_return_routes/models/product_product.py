# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, fields, models, _


class Product(models.Model):
    _inherit = 'product.product'

    def update_routes_after_return_to_stock(self):
        # Get routes via helpers from another module
        mto_route = self.env['product.template']._get_mto_route()
        mto_mts_route = self.env['product.template']._get_mto_mts_route()
        updated_products = self.env['product.product']
        # Change MTO routes to MTO+MTS
        for product in self:
            route_ids = product.route_ids
            if mto_route in route_ids and not mto_mts_route in route_ids:
                route_ids -= mto_route
                route_ids += mto_mts_route
                product.message_post(
                    body=_(
                        'Route <small><b>%s</b></small> replaced with '
                        'route <small><b>%s</b></small> while '
                        'processing unbuild %s.'
                    ) % (mto_route.name, mto_mts_route.name, product.name)
                )
                product.route_ids = route_ids
                updated_products += product
        return updated_products
