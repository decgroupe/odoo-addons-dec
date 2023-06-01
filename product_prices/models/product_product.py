# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2020

import json

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Override digit field to increase precision and track changes
    standard_price = fields.Float(
        digits="Purchase Price",
        tracking=True,
    )

    def write(self, vals):
        now = fields.Datetime.now()
        if "list_price" in vals:
            vals["price_write_date"] = fields.Datetime.now()
            vals["price_write_uid"] = self.env.user.id
        if "standard_price" in vals:
            vals["standard_price_write_date"] = fields.Datetime.now()
            vals["standard_price_write_uid"] = self.env.user.id
        res = super().write(vals)
        return res

    def open_price_graph(self):
        self.ensure_one()
        act = self.env.ref("product_prices.act_window_product_price_graph")
        action = act.read()[0]
        context = json.loads(action["context"])
        context.update(
            {
                "active_model": self._name,
                "active_id": self.id,
                "active_ids": self.ids,
            }
        )
        action["context"] = json.dumps(context)

        # action = self.env.ref('product_prices.act_window_product_price_graph'
        #                      ).read()[0]
        return action
