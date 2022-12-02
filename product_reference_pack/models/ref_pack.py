# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class RefPack(models.Model):
    """ Description """

    _name = 'ref.pack'
    _description = 'Pack'
    _rec_name = 'name'

    # TODO: Step 1 : Rename to product_tmpl_id
    product_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        required=True,
        copy=False,
    )
    # TODO: Step 2 : Rename to product_id
    product_variant_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        copy=False,
        compute='_compute_product_variant_id',
        inverse='_inverse_product_variant_id',
        compute_sudo=True,
        store=False,
    )
    name = fields.Char(
        related='product_id.name',
        string='Name',
    )
    default_code = fields.Char(
        related='product_id.default_code',
        string='Code',
    )
    public_code = fields.Char(
        related='product_id.public_code',
        string='Public Code',
    )
    list_price = fields.Float(
        related='product_id.list_price',
        string='Sale Price',
    )
    standard_price = fields.Float(
        related='product_id.standard_price',
        string='Cost Price',
    )
    type = fields.Selection(
        [('company', 'Company'), ('manufacturer', 'Manufacturer')],
        'Pack Type',
        required=True,
    )

    @api.model
    def create(self, vals):
        if vals.get('product_id'):
            product_tmpl_id = self.env['product.template'].browse(
                vals.get('product_id')
            )
        elif vals.get('product_variant_id'):
            product_variant_id = vals.get('product_variant_id')
            product_tmpl_id = self.env['product.product'].browse(
                product_variant_id
            ).product_tmpl_id
        else:
            product_tmpl_id = False

        if product_tmpl_id:
            vals['product_id'] = product_tmpl_id.id
        ref_pack = super().create(vals)
        ref_pack._set_product_tmpl_default_values()
        return ref_pack

    def _set_product_tmpl_default_values(self):
        for rec in self:
            rec.product_id.pack_ok = True
            rec.product_id.pack_type = 'detailed'
            rec.product_id.pack_component_price = 'ignored'
            rec.product_id.pack_modifiable = False
            if rec.product_id.sale_ok and rec.product_id.purchase_ok:
                rec.product_id.pack_order_type = 'all'
            elif rec.product_id.sale_ok:
                rec.product_id.pack_order_type = 'sale'
            elif rec.product_id.purchase_ok:
                rec.product_id.pack_order_type = 'purchase'

    @api.depends('product_id', 'product_id.product_variant_id')
    def _compute_product_variant_id(self):
        for rec in self:
            rec.product_variant_id = rec.with_context(
                active_test=False
            ).product_id.product_variant_id.id
            _logger.debug(
                "%d  %d  %d", rec.id, rec.product_id.id,
                rec.product_variant_id.id
            )

    def _inverse_product_variant_id(self):
        for rec in self:
            rec.product_id = rec.with_context(
                active_test=False
            ).product_variant_id.product_tmpl_id
