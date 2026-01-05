# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Mimic pricelist_id field from sale.order model
    # Lock type to purchase using domain attribute
    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Pricelist",
        compute="_compute_pricelist_id",
        store=True,
        readonly=False,
        precompute=True,
        check_company=True,  # Unrequired company
        domain="[('type', '=', 'purchase'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",  # noqa: E501
        tracking=1,
        help="Pricelist for current purchase order.",
    )

    @api.depends("partner_id", "company_id")
    def _compute_pricelist_id(self):
        for order in self:
            if order.state != "draft":
                continue
            if not order.partner_id:
                order.pricelist_id = False
                continue
            order = order.with_company(order.company_id)
            order.pricelist_id = order.partner_id.property_product_pricelist_purchase

    @api.onchange("pricelist_id")
    def onchange_pricelist_id(self):
        self.action_recompute_all_lines()

    def action_recompute_all_lines(self):
        for order in self:
            for line in order.order_line:
                line._compute_price_unit_and_date_planned_and_name()
