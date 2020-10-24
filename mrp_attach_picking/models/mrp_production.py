# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    allow_attach_picking = fields.Boolean(
        compute='_allow_attach_picking',
        help="Technical field used to hide attach picking action if "
        "production order is already linked to picking"
    )

    @api.multi
    def _allow_attach_picking(self):
        for production in self:
            move_dest_ids = production.move_finished_ids.mapped(
                'move_dest_ids'
            )
            if not move_dest_ids:
                production.allow_attach_picking = True
