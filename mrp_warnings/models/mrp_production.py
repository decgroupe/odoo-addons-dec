# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Aug 2020

from odoo import api, models, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, values):
        if values.get('bom_id'):
            bom_id = self.env['mrp.bom'].browse(values.get('bom_id'))
            self._check_bom_warnings(bom_id)
        production = super(MrpProduction, self).create(values)
        return production

    def _check_bom_warnings(self, bom_id):
        errors = []
        for line in bom_id.bom_line_ids:
            errors += self._check_bom_line_product(line.product_id)
        if errors:
            errors = ['\n'] + errors
            raise UserError(
                _(
                    'Cannot manufacture product {}, because of '
                    'following error(s):'
                    '{}'
                ).format(bom_id.product_id.display_name, '\n - '.join(errors))
            )

    def _check_bom_line_product(self, product_id):
        res = []
        if not product_id.active:
            res.append(_('{} is archived').format(product_id.display_name))
        if product_id.state == 'obsolete':
            res.append(_('{} is obsolete').format(product_id.display_name))
        return res
