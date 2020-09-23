# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Aug 2020

from itertools import product
from odoo import api, models, _
from odoo.exceptions import UserError


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.multi
    def _run_manufacture(
        self, product_id, product_qty, product_uom, location_id, name, origin,
        values
    ):
        warnings = self._check_run_manufacture_warnings(
            product_id, product_qty, product_uom, location_id, name, origin,
            values
        )
        if warnings:
            raise UserError('\n'.join(warnings))

        return super()._run_manufacture(
            product_id, product_qty, product_uom, location_id, name, origin,
            values
        )

    def _check_run_manufacture_warnings(
        self, product_id, product_qty, product_uom, location_id, name, origin,
        values
    ):
        res = []
        try:
            self._check_product_active(product_id)
            self._check_product_state(product_id)
        except UserError as error:
            res.append(error.name)
        try:
            self._check_empty_product_bom(product_id, values)
        except UserError as error:
            res.append(error.name)
        return res

    def _check_product_state(self, product_id):
        if product_id.state not in ['draft', 'sellable']:
            state_desc = dict(
                product_id._fields['state']._description_selection(self.env)
            )
            raise UserError(
                _(
                    'Cannot manufacture product %s, state is "%s". '
                    'Please change its state to "%s" or "%s".'
                ) % (
                    product_id.display_name,
                    state_desc.get(product_id.state),
                    state_desc.get('draft'),
                    state_desc.get('sellable'),
                )
            )

    def _check_empty_product_bom(self, product_id, values):
        bom = self._get_matching_bom(product_id, values)
        if bom and not bom.bom_line_ids:
            raise UserError(
                _(
                    'Bill of Material %s is empty for the product %s. '
                    'Please add at least one component to this Bill of Material.'
                ) % (
                    bom.code or str(bom.id),
                    product_id.display_name,
                )
            )
