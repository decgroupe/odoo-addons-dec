# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2020


import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("Creating pricelist with values: %s", vals_list)
        return super().create(vals_list)

    def write(self, vals):
        _logger.info("Updating pricelist %s with values: %s", self.ids, vals)
        return super().write(vals)

    def unlink(self):
        _logger.info("Deleting pricelist with ids: %s", self.ids)
        return super().unlink()

    def action_view_pricelist_items(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "product_pricelist_analysis.act_window_product_pricelist_item"
        )
        action["context"] = dict(self.env.context)
        action["context"]["search_default_pricelist_id"] = self.id
        return action
