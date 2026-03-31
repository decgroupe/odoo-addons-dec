# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import models

from odoo.addons.tools_miscellaneous.tools.html_helper import div, ul


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def _generate_produce_moves(self):
        """Override to update MTO routes and link produced moves to consumed moves."""
        self.ensure_one()
        moves = super()._generate_produce_moves()
        # update routes for products returning to stock
        ids = moves.mapped("product_id").update_routes_after_return_to_stock(self.name)
        edited_products = self.env["product.product"].browse(ids)
        if edited_products:
            title = self.env._("Following product's routes has been edited:")
            product_lines = []
            for product_name in edited_products.mapped("display_name"):
                product_lines.append(f"<li>{product_name}</li>")
            body = div(title) + ul("".join(product_lines))
            self.message_post(body=body)
        # link produced moves to consumed moves for traceability
        for move in moves:
            move.move_orig_ids = self.consume_line_ids
        return moves
