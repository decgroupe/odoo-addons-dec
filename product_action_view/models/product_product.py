# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def action_view_base(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "product.product_normal_action"
        )
        return action

    def action_view(self):
        action = self.action_view_base()
        form = self.env.ref("product.product_normal_form_view")
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            tree = self.env.ref("product.product_product_tree_view")
            action["domain"] = [("id", "in", self.ids)]
            action["views"] = [(tree.id, "tree"), (form.id, "form")]
            action["view_mode"] = "tree,form"
        else:
            action["views"] = [(form.id, "form")]
            action["view_mode"] = "form"
            action["res_id"] = self.ids[0]
        return action

    def action_view_template(self):
        action = self.mapped("product_tmpl_id").action_view()
        return action

    def action_view_variants(self):
        return self.action_view()
