# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

import logging

from odoo import api, fields, models
from odoo.tools.misc import split_every
from odoo.tools.progressbar import progressbar as pb
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class ChangeProductStateByCategory(models.TransientModel):
    _name = "change.product.state.by.category"
    _description = "Customize purchase report"

    category_id = fields.Many2one(
        comodel_name="product.category",
    )
    state_id = fields.Many2one(
        comodel_name="product.state",
        string="New Status",
    )
    domain = fields.Char(
        string="Apply on",
        default="[]",
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        # active_ids = self.env.context.get('active_ids')
        return res

    def action_update_state(self):
        self.ensure_one()
        ProductProduct = self.env["product.product"]
        ProductTemplate = self.env["product.template"]
        if self.state_id:
            search_domain = safe_eval(self.domain)
            product_ids = ProductProduct.search(search_domain)
            ids = product_ids.mapped("product_tmpl_id").ids
            SPLIT = 500
            idx = 0
            for chunck_ids in pb(list(split_every(SPLIT, ids))):
                _logger.info(
                    "Processing (%d -> %d)/%d",
                    idx,
                    min(idx + SPLIT, len(ids)),
                    len(ids),
                )
                idx += SPLIT
                ProductTemplate.with_context(prefetch_fields=False).browse(
                    chunck_ids
                ).write({"product_state_id": self.state_id.id})

    @api.onchange("category_id")
    def _onchange_category_id(self):
        if self.category_id:
            self.domain = "[('categ_id', 'child_of', %s)]" % (self.category_id.id,)
        else:
            self.domain = "[]"
