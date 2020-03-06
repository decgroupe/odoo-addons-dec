# -*- encoding: utf-8 -*-

import time

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_academy = fields.Many2one(
        'res.partner.academy',
        'Academy',
        help="Educational academy of the current partner.",
    )
    #zip = fields.Char(related='address.zip', string='Zip')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # Make a search with default criteria
        names = super().name_search(name=name,
                                    args=args,
                                    operator=operator,
                                    limit=limit)

        # Add city and zip to quickly identify a partner
        result = []
        for item in names:
            #item = list(item)
            partner = self.browse(item[0])[0]
            # Don't reuse item[1] lazy result as it contains line feeds with address
            override_name_get = ('%s (%s %s)') % (partner.name, partner.zip, partner.city)
            result.append((item[0], override_name_get))

        return result
