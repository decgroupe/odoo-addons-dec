# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    state = fields.Selection(
        selection=[
            ('quotation', 'In Quotation'),
            ('draft', 'In Development'),
            ('review', 'Need review'),
            ('sellable', 'Normal'),
            ('end', 'End of Lifecycle'),
            ('obsolete', 'Obsolete'),
        ],
        string='Status',
        default='sellable',
        index=True,
        tracking=True,
    )

    def write(self, vals):
        # Auto set state to obsolete when archiving a product
        if 'active' in vals and not vals.get('active'):
            vals['state'] = 'obsolete'
        res = super().write(vals)
        return res
