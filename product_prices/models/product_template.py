# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2020

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.tools.progressbar import progressbar as pb

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Override digit field to increase precision and track changes
    standard_price = fields.Float(
        digits="Purchase Price",
        tracking=True,
    )
    # Override to track changes
    list_price = fields.Float(tracking=True)

    standard_price_po_uom = fields.Float(
        string="Cost (Purchase UoM)",
        compute="_compute_standard_price_po_uom",
        inverse="_set_standard_price_po_uom",
        digits="Product Price",
        groups="base.group_user",
        help='Same field than standard_price but expressed in "Purchase Unit '
        'of Measure".',
    )
    # Used only to hide standard_price_po_uom field from view if not needed
    same_uom = fields.Boolean(
        compute="_compute_same_uom",
        store=True,
        compute_sudo=True,
        help='Are "Default Unit of Measure" and "Purchase Unit of Measure" '
        "identical ?",
    )
    default_purchase_price = fields.Monetary(
        compute="_compute_default_purchase_price",
        string="Purchase Price (Default UoM)",
        digits="Purchase Price",
        help="Purchase price based on default seller pricelist computed with "
        '"Default Unit of Measure"',
    )
    default_purchase_price_graph = fields.Char(
        compute="_compute_default_purchase_price",
        string="Purchase Price Graph (Default UoM)",
    )
    default_purchase_price_po_uom = fields.Monetary(
        compute="_compute_default_purchase_price",
        string="Purchase Price",
        digits="Purchase Price",
        help="Purchase price based on default seller pricelist computed with "
        '"Purchase Unit of Measure"',
    )
    default_purchase_price_graph_po_uom = fields.Char(
        compute="_compute_default_purchase_price",
        string="Purchase Price Graph",
    )
    default_sell_price = fields.Monetary(
        compute="_compute_default_sell_price",
        string="Sell Price",
        digits="Product Price",
        help="Sell price based on default sell pricelist",
    )
    default_sell_price_graph = fields.Char(
        compute="_compute_default_sell_price",
        string="Sell Price Graph",
    )
    pricelist_bypass = fields.Boolean(
        string="By-pass",
        help="A bypass action will create a pricelist item to overwrite "
        "pricelist computation",
    )
    pricelist_bypass_item = fields.Many2one(
        comodel_name="product.pricelist.item",
        string="Pricelist item",
    )
    market_place = fields.Boolean(
        string="Market place",
        help="Tip to know if the product must be displayed on the market place",
    )
    price_write_date = fields.Datetime("Price write date")
    price_write_uid = fields.Many2one(
        comodel_name="res.users",
        string="Price last editor",
    )
    standard_price_write_date = fields.Datetime("Standard price write date")
    standard_price_write_uid = fields.Many2one(
        comodel_name="res.users",
        string="Standard price last editor",
    )

    @api.onchange("standard_price_po_uom")
    def onchange_standard_price_po_uom(self):
        self._set_standard_price_po_uom()

    @api.depends("standard_price", "uom_id", "uom_po_id")
    def _compute_standard_price_po_uom(self):
        self.standard_price_po_uom = 0.0
        # Check that uom_id is not False (possibility in editing mode)
        for product in self.filtered("uom_id"):
            price = product.uom_id._compute_price(
                product.standard_price,
                product.uom_po_id,
            )
            _logger.debug("New standard_price_po_uom = {}".format(price))
            product.standard_price_po_uom = price

    def _set_standard_price_po_uom(self):
        # Check that uoms are not False (possibility in editing mode)
        for product in self.filtered("uom_po_id").filtered("uom_id"):
            price = product.uom_po_id._compute_price(
                product.standard_price_po_uom,
                product.uom_id,
            )
            _logger.debug("New standard_price = {}".format(price))
            product.standard_price = price

    @api.depends("uom_id", "uom_po_id")
    def _compute_same_uom(self):
        for product in self:
            product.same_uom = product.uom_id.id == product.uom_po_id.id

    @api.onchange("list_price", "standard_price", "uom_id", "uom_po_id")
    def onchange_prices(self):
        self._compute_default_purchase_price()

    @api.depends(
        "seller_id",
        "standard_price",
        "uom_id",
        "uom_po_id",
    )
    def _compute_default_purchase_price(self):
        self.default_purchase_price = 0
        self.default_purchase_price_graph = False
        self.default_purchase_price_po_uom = 0
        self.default_purchase_price_graph_po_uom = False
        for rec in pb(self):
            seller_id = rec.main_seller_id
            if rec.main_seller_id:
                rec.default_purchase_price = seller_id.list_price_unit
                rec.default_purchase_price_graph = seller_id.list_price_unit_graph
                rec.default_purchase_price_po_uom = seller_id.list_price
                rec.default_purchase_price_graph_po_uom = seller_id.list_price_graph
            else:
                msg = "No default seller assigned to this product (missing 'main_seller_id')"
                graph = []
                rec.default_purchase_price = rec.standard_price
                rec.default_purchase_price_graph = "\n".join(graph)
                rec.default_purchase_price_po_uom = rec.standard_price_po_uom
                rec.default_purchase_price_graph_po_uom = "\n".join(graph)

    @api.depends(
        "company_id",
        "list_price",
        "standard_price",
        "uom_id",
    )
    def _compute_default_sell_price(self):
        self.default_sell_price = 0
        self.default_sell_price_graph = False
        history = {}
        for product in pb(self):
            if isinstance(product.id, models.NewId):
                continue
            qty = 1.0
            partner = False
            hkey = (product, qty, partner)
            self.env["product.pricelist"]._ensure_history_struct(history, hkey)
            company_id = product.company_id or self.env.company
            if company_id and company_id.partner_id:
                pricelist = (
                    company_id.partner_id.property_product_pricelist.with_context(
                        history=history
                    )
                )
                if pricelist:
                    product.default_sell_price = pricelist.get_product_price(
                        product, qty, partner, uom_id=product.uom_id.id
                    )

            else:
                product.default_sell_price = product.list_price
                self.env["product.pricelist"].with_context(
                    history=history
                )._addto_history(
                    hkey,
                    message="No company assigned to this product "
                    "(missing 'property_product_pricelist')",
                    action="end",
                )
            graph = history[hkey]["graph"]["header"] + history[hkey]["graph"]["body"]
            product.default_sell_price_graph = "\n".join(graph)

    def _get_pricelist_search_domain(self):
        return [("type", "=", "sale")]

    def _get_pricelist_items_search_domain(self, pricelists):
        # Currently, we just assert that there is only one variant.
        product_id = self.product_variant_id
        return [
            ("pricelist_id", "in", pricelists.ids),
            "|",
            ("product_tmpl_id", "=", self.id),
            ("product_id", "=", product_id.id),
        ]

    def _prepare_bypass_rule(self, pricelists):
        # Currently, we just assert that there is only one variant.
        product_id = self.product_variant_id
        return {
            "sequence": 2,
            "note": _("By-pass {}").format(self.default_code),
            "pricelist_id": pricelists.ids[0],
            "product_tmpl_id": self.id,
            "product_id": product_id.id,
            "compute_price": "formula",
            "applied_on": "1_product",
            "base": "list_price",
            "company_id": self.company_id.id,
        }

    def update_bypass(self, state):
        Pricelist = self.env["product.pricelist"]
        PricelistItem = self.env["product.pricelist.item"]
        for product_tmpl_id in self:
            pricelists = Pricelist.search(self._get_pricelist_search_domain())
            pricelist_items = PricelistItem.search(
                self._get_pricelist_items_search_domain(pricelists)
            )
            if state:
                if not pricelist_items:
                    data = self._prepare_bypass_rule(pricelists)
                    product_tmpl_id.pricelist_bypass_item = PricelistItem.create(data)
            else:
                if len(pricelist_items) > 1:
                    raise UserError(
                        _(
                            "Too many pricelist items for this product!, only "
                            "one sale pricelist item must exist for this "
                            "product to disable by-pass functionality"
                        )
                    )
                elif pricelist_items:
                    pricelist_items.unlink()

    def write(self, vals):
        if "list_price" in vals:
            vals["price_write_date"] = fields.Datetime.now()
            vals["price_write_uid"] = self.env.user.id
        if "standard_price" in vals:
            vals["standard_price_write_date"] = fields.Datetime.now()
            vals["standard_price_write_uid"] = self.env.user.id
        if "pricelist_bypass" in vals:
            self.update_bypass(state=vals["pricelist_bypass"])
        res = super().write(vals)
        return res

    def open_price_graph(self):
        self.ensure_one()
        # TODO: Open a wizard, first, to select the variant that will be used
        # to compute the graph.
        # Currently, we just assert that there is only one variant.
        action = self.product_variant_id.open_price_graph()
        return action
