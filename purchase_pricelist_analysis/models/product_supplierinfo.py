# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    list_price_graph = fields.Char(
        compute="_compute_list_price",
        string="Computation Graph",
    )
    list_price_steps = fields.Char(
        compute="_compute_list_price",
        string="Computation Steps",
    )

    def _compute_list_price(self):
        history = {}
        super(ProductSupplierinfo, self.with_context(history=history))._compute_list_price()
        self.list_price_graph = False
        self.list_price_steps = False
        for rec in self:
            # Product can be a template or a variant
            product_id = rec.product_id or rec.product_tmpl_id
            # Convert quantities to default product UoM
            qty = rec.product_uom._compute_quantity(rec.min_qty or 1.0, product_id.uom_id)
            partner = rec.name
            hkey = (product_id, qty, partner)
            if hkey in history:
                graph = (
                    history[hkey]["graph"]["header"] + history[hkey]["graph"]["body"]
                )
                rec.list_price_graph = "\n".join(graph)
                steps = history[hkey]["steps"]
                rec.list_price_steps = "\n".join(steps)
