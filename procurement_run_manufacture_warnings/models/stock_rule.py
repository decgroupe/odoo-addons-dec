# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020


from odoo import models
from odoo.exceptions import UserError

from odoo.addons.stock.models.stock_rule import ProcurementException


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_manufacture(self, procurements):
        warnings = self._check_run_manufacture_warnings(procurements)
        if warnings:
            raise ProcurementException(warnings)
        return super()._run_manufacture(procurements)

    def _check_run_manufacture_warnings(self, procurements):
        errors = []
        for procurement, _rule in procurements:
            try:
                self._check_product_active(procurement.product_id)
                self._check_product_state(procurement.product_id)
            except UserError as error:
                errors.append((procurement, str(error)))
            try:
                self._check_no_or_empty_product_bom(
                    procurement.product_id, procurement.company_id, procurement.values
                )
            except UserError as error:
                errors.append((procurement, str(error)))
        return errors

    def _check_product_active(self, product_id):
        if not product_id.active:
            raise UserError(
                self.env._(
                    "Cannot manufacture product %(name)s, because it is archived. ",
                    name=product_id.display_name,
                )
            )

    def _check_product_state(self, product_id):
        if product_id.state not in ["draft", "sellable"]:
            ProductState = self.env["product.state"]
            state_draft = ProductState.search([("code", "=", "draft")], limit=1)
            state_sellable = ProductState.search([("code", "=", "sellable")], limit=1)
            raise UserError(
                self.env._(
                    'Cannot manufacture product %(name)s, state is "%(state)s".\n'
                    'Please change its state to "%(draft)s" or "%(sellable)s".',
                    name=product_id.display_name,
                    state=product_id.product_state_id.name,
                    draft=state_draft.name,
                    sellable=state_sellable.name,
                )
            )

    def _check_no_or_empty_product_bom(self, product_id, company_id, values):
        bom = self._get_matching_bom(product_id, company_id, values)
        if not bom:
            raise UserError(
                self.env._(
                    "There is no Bill of Material found for the product %(name)s. "
                    "Please define a Bill of Material for this product.",
                    name=product_id.display_name,
                )
            )
        if not bom.bom_line_ids:
            raise UserError(
                self.env._(
                    "Bill of Material %(bom)s is empty for the product %(product)s.\n"
                    "Please add at least one component to this Bill of Material.",
                    bom=bom.code or str(bom.id),
                    product=product_id.display_name,
                )
            )
