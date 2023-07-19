# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020


from odoo import _, models
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.exceptions import UserError


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_manufacture(self, procurements):
        warnings = self._check_run_manufacture_warnings(procurements)
        if warnings:
            raise ProcurementException(warnings)
        return super()._run_manufacture(procurements)

    def _check_run_manufacture_warnings(self, procurements):
        errors = []
        for procurement, rule in procurements:
            try:
                self._check_product_active(procurement.product_id)
                self._check_product_state(procurement.product_id)
            except UserError as error:
                errors.append((procurement, error.name))
            try:
                self._check_empty_product_bom(
                    procurement.product_id, procurement.company_id, procurement.values
                )
            except UserError as error:
                errors.append((procurement, error.name))
        return errors

    def _check_product_active(self, product_id):
        if not product_id.active:
            raise UserError(
                _("Cannot manufacture product %s, because it is archived. ")
                % (product_id.display_name,)
            )

    def _check_product_state(self, product_id):
        if product_id.state not in ["draft", "sellable"]:
            state_desc = dict(
                product_id._fields["state"]._description_selection(self.env)
            )
            raise UserError(
                _(
                    'Cannot manufacture product %s, state is "%s". '
                    'Please change its state to "%s" or "%s".'
                )
                % (
                    product_id.display_name,
                    state_desc.get(product_id.state),
                    state_desc.get("draft"),
                    state_desc.get("sellable"),
                )
            )

    def _check_empty_product_bom(self, product_id, company_id, values):
        bom = self._get_matching_bom(product_id, company_id, values)
        if bom and not bom.bom_line_ids:
            raise UserError(
                _(
                    "Bill of Material %s is empty for the product %s. "
                    "Please add at least one component to this Bill of Material."
                )
                % (
                    bom.code or str(bom.id),
                    product_id.display_name,
                )
            )
