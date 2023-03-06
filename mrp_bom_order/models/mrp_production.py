# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    newer_bom_id = fields.Many2one(
        'mrp.bom',
        'Newer BoM',
        compute='_compute_newer_bom_id',
    )

    @api.depends('bom_id', 'product_id')
    def _compute_newer_bom_id(self):
        self.newer_bom_id = False
        for production in self.filtered("product_id"):
            bom_id = self.env['mrp.bom']._bom_find(
                product=production.product_id
            )
            if bom_id and production.bom_id != bom_id:
                production.newer_bom_id = bom_id
