# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # Make a search with default criteria
        names = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        # Add city and zip to quickly identify a partner
        result = []
        for item in names:
            partner = self.browse(item[0])[0]
            # Don't reuse item[1] lazy result as it contains line feeds with address
            override_name_get = ('%s (%s %s)'
                                ) % (item[1], partner.zip, partner.city)
            result.append((item[0], override_name_get))
        return result
