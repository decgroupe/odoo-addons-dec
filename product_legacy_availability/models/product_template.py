# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    legacy_qty_available = fields.Float(
        compute='_compute_product_template_available',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Quantity On Hand (legacy)',
        help="Current quantity of products.\n"
        "In a context with a single Stock Location, this includes "
        "goods stored at this Location, or any of its children.\n"
        "In a context with a single Warehouse, this includes "
        "goods stored in the Stock Location of this Warehouse, or any "
        "of its children.\n"
        "In a context with a single Shop, this includes goods "
        "stored in the Stock Location of the Warehouse of this Shop, "
        "or any of its children.\n"
        "Otherwise, this includes goods stored in any Stock Location "
        "typed as 'internal'."
    )

    legacy_virtual_available = fields.Float(
        compute='_compute_product_template_available',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Quantity Available (legacy)',
        help="Forecast quantity (computed as Quantity On Hand "
        "- Outgoing + Incoming)\n"
        "In a context with a single Stock Location, this includes "
        "goods stored at this Location, or any of its children.\n"
        "In a context with a single Warehouse, this includes "
        "goods stored in the Stock Location of this Warehouse, or any "
        "of its children.\n"
        "In a context with a single Shop, this includes goods "
        "stored in the Stock Location of the Warehouse of this Shop, "
        "or any of its children.\n"
        "Otherwise, this includes goods stored in any Stock Location "
        "typed as 'internal'."
    )

    legacy_incoming_qty = fields.Float(
        compute='_compute_product_template_available',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Incoming (legacy)',
        help="Quantity of products that are planned to arrive.\n"
        "In a context with a single Stock Location, this includes "
        "goods arriving to this Location, or any of its children.\n"
        "In a context with a single Warehouse, this includes "
        "goods arriving to the Stock Location of this Warehouse, or "
        "any of its children.\n"
        "In a context with a single Shop, this includes goods "
        "arriving to the Stock Location of the Warehouse of this "
        "Shop, or any of its children.\n"
        "Otherwise, this includes goods arriving to any Stock "
        "Location typed as 'internal'."
    )

    legacy_outgoing_qty = fields.Float(
        compute='_compute_product_template_available',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Outgoing (legacy)',
        help="Quantity of products that are planned to leave.\n"
        "In a context with a single Stock Location, this includes "
        "goods leaving from this Location, or any of its children.\n"
        "In a context with a single Warehouse, this includes "
        "goods leaving from the Stock Location of this Warehouse, or "
        "any of its children.\n"
        "In a context with a single Shop, this includes goods "
        "leaving from the Stock Location of the Warehouse of this "
        "Shop, or any of its children.\n"
        "Otherwise, this includes goods leaving from any Stock "
        "Location typed as 'internal'."
    )

    @api.depends(
        'product_variant_ids', 'product_variant_ids.legacy_qty_available',
        'product_variant_ids.legacy_virtual_available',
        'product_variant_ids.legacy_incoming_qty',
        'product_variant_ids.legacy_outgoing_qty'
    )
    def _compute_product_template_available(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.legacy_qty_available = template.product_variant_ids.legacy_qty_available
            template.legacy_virtual_available = template.product_variant_ids.legacy_virtual_available
            template.legacy_incoming_qty = template.product_variant_ids.legacy_incoming_qty
            template.legacy_outgoing_qty = template.product_variant_ids.legacy_outgoing_qty
        for template in (self - unique_variants):
            template.legacy_qty_available = 0.0
            template.legacy_virtual_available = 0.0
            template.legacy_incoming_qty = 0.0
            template.legacy_outgoing_qty = 0.0

    @api.multi
    def action_update_stock_quant_availability(self):
        product_variant_ids = self.with_context(active_test=False).\
            mapped('product_variant_ids')
        product_variant_ids.action_update_stock_quant_availability()
        self.update_qty_available_cache()
