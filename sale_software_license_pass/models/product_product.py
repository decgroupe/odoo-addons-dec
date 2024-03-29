# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import fields, models, api


class Product(models.Model):
    _inherit = "product.product"

    license_pack_id = fields.Many2one(
        comodel_name='software.license.pack',
        string='Application Pack',
        help='Pack used to generate a new Application Pass.'
    )

    @api.onchange('service_tracking')
    def _onchange_service_tracking(self):
        """This mimicks upstream core that duplicates this code."""
        res = super()._onchange_service_tracking()
        if self.service_tracking != 'create_application_pass':
            self.license_pack_id = False
        return res
