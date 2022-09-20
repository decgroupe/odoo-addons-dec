# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models, api


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    landmark = fields.Char('Landmark')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Supplier',
    )
    supplier_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Supplier",
        compute="_compute_supplier_info",
    )
    delay = fields.Integer(
        string='Delay',
        compute="_compute_delay",
        inverse="_inverse_delay",
        help="Produce lead time in days if the product have to be "
        "manufactured or delivery lead time in days if the product have to "
        "be purchased."
    )

    @api.multi
    def _get_supplierinfo(self):
        """Given a BoM line, return the supplierinfo that matches
        with product and partner, if exist"""
        self.ensure_one()
        # Get supplier info from current partner_id
        supplierinfos = self.product_id.seller_ids.filtered(
            lambda s: (
                s.product_id == self.product_id \
                and s.name == self.partner_id
            )
        )
        # Try again if product variant is enabled
        if not supplierinfos:
            supplierinfos = self.product_id.seller_ids.filtered(
                lambda s: (
                    s.product_tmpl_id == self.product_tmpl_id \
                    and s.name == self.partner_id
                )
            )
        return supplierinfos and supplierinfos[0] or False

    @api.depends("partner_id")
    def _compute_supplier_info(self):
        for rec in self:
            rec.supplier_id = rec._get_supplierinfo()

    @api.depends(
        "product_id.supply_method", "product_id.procure_method", "supplier_id"
    )
    def _compute_delay(self):
        for rec in self:
            if rec.product_id.procure_method == 'make_to_order':
                if rec.product_id.supply_method == 'buy':
                    rec.delay = rec.supplier_id.delay
                elif rec.product_id.supply_method == 'produce':
                    rec.delay = rec.product_id.produce_delay
            elif rec.product_id.procure_method == 'make_to_stock':
                rec.delay = 0

    def _inverse_delay(self):
        for rec in self:
            if rec.product_id.procure_method == 'make_to_order':
                if rec.product_id.supply_method == 'buy':
                    if rec.supplier_id:
                        rec.supplier_id.delay = rec.delay
                elif rec.product_id.supply_method == 'produce':
                    rec.product_id.produce_delay = rec.delay
