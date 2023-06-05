# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2020

from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    # This method is a copy/paste of the one in:
    #   ./addons/product/models/product_pricelist.py
    # except that the SQL query is hooked to add sequence in ORDER BY.
    # DO NOT SAVE this file with auto-format, keep original format to
    # follow modifications from original method.

    def _compute_price_rule_get_items(
        self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids
    ):
        res = super()._compute_price_rule_get_items(
            products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids
        )
        # yapf: disable
        self.ensure_one()
        # Load all rules
        self.env['product.pricelist.item'].flush(['price', 'currency_id', 'company_id', 'active'])
        self.env.cr.execute(
            """
            SELECT
                item.id
            FROM
                product_pricelist_item AS item
            LEFT JOIN product_category AS categ ON item.categ_id = categ.id
            WHERE
                (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                AND (item.product_id IS NULL OR item.product_id = any(%s))
                AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                AND (item.pricelist_id = %s)
                AND (item.date_start IS NULL OR item.date_start<=%s)
                AND (item.date_end IS NULL OR item.date_end>=%s)
                AND (item.active = TRUE)
            ORDER BY
                item.sequence, item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc
            """,
            (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))
        # NOTE: if you change `order by` on that query, make sure it matches
        # _order from model to avoid inconstencies and undeterministic issues.

        item_ids = [x[0] for x in self.env.cr.fetchall()]
        res = self.env['product.pricelist.item'].browse(item_ids)
        # yapf: enable
        return res
