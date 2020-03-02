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
            item = list(item)
            data = self.read(item[0], ['city', 'zip'])
            if data['zip'] and data['city']:
                item[1] = ('%s (%s %s)') % (item[1], data['zip'], data['city'])
            result.append(item)

        return result
