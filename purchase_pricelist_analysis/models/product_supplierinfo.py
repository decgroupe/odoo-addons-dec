# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    list_price_graph = fields.Char(
        compute="_compute_list_price",
        string="Computation Graph",
        help="Mermaid type graph to explain seller price computation (Purchase UoM)",
    )
    list_price_steps = fields.Char(
        compute="_compute_list_price",
        string="Computation Steps",
        help="Text enumeration to explain seller price computation (Purchase UoM)",
    )
    list_price_unit_graph = fields.Char(
        compute="_compute_list_price_unit",
        string="Computation Graph (Default UoM) ",
        help="Mermaid type graph to explain seller price computation (Default UoM)",
    )
    list_price_unit_steps = fields.Char(
        compute="_compute_list_price_unit",
        string="Computation Steps (Default UoM)",
        help="Text enumeration to explain seller price computation (Default UoM)",
    )

    def _get_graph_steps(self, history):
        self.ensure_one()
        # Product can be a template or a variant
        product_id = self.product_id or self.product_tmpl_id
        # Convert quantities to default product UoM
        qty = self.product_uom._compute_quantity(self.min_qty or 1.0, product_id.uom_id)
        partner = self.name
        hkey = (product_id, qty, partner)
        if not self.name.property_product_pricelist_purchase:
            msg = (
                "No purchase pricelist found for seller '%s'"
                "(missing 'property_product_pricelist_purchase')" % (self.display_name)
            )
            self.env["product.pricelist"].with_context(history=history)._addto_history(
                hkey, message=msg, action="end"
            )
        if hkey in history:
            graph = history[hkey]["graph"]["header"] + history[hkey]["graph"]["body"]
            steps = history[hkey]["steps"]
            return "\n".join(graph), "\n".join(steps)
        return False, False

    def _compute_list_price(self):
        history = {}
        super(
            ProductSupplierinfo, self.with_context(history=history)
        )._compute_list_price()
        for rec in self:
            rec.list_price_graph, rec.list_price_steps = rec._get_graph_steps(history)

    def _compute_list_price_unit(self):
        history = {}
        super(
            ProductSupplierinfo, self.with_context(history=history)
        )._compute_list_price_unit()
        for rec in self:
            rec.list_price_unit_graph, rec.list_price_unit_steps = rec._get_graph_steps(
                history
            )
