# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, July 2020

from odoo import models, api, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    production_ids = fields.Many2many(
        'mrp.production',
        compute='_compute_production_ids',
        string='Manufacturing orders associated to this picking',
    )
    production_count = fields.Integer(
        compute='_compute_production_ids',
        string='Manufacturing Orders',
    )

    @api.depends('group_id')
    def _compute_production_ids(self):
        for picking in self:
            picking.production_ids = self.env['mrp.production'].search(
                [
                    ('procurement_group_id', '=', picking.group_id.id),
                    ('procurement_group_id', '!=', False),
                ]
            )
            picking.production_count = len(picking.production_ids)
