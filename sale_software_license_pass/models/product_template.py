# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    service_tracking = fields.Selection(
        selection_add=[
            ("create_application_pass", "Create an application pass")
        ],
    )
    license_pack_id = fields.Many2one(
        related='product_variant_ids.license_pack_id',
        readonly=False,
    )

    def write(self, vals):
        """We remove from product.product to avoid error."""
        _vals = vals.copy()
        if vals.get('license_pack_id', False):
            self.product_variant_ids.write(
                {
                    'license_pack_id':
                        vals.get('license_pack_id')
                }
            )
            _vals.pop('license_pack_id')
        return super().write(_vals)

    @api.onchange('service_tracking')
    def _onchange_service_tracking(self):
        """Reset project when using this setting."""
        res = super()._onchange_service_tracking()
        if self.service_tracking != 'create_application_pass':
            self.license_pack_id = False
        return res
