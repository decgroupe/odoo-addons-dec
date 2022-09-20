# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def action_view_base(self):
        return self.env.ref('product.product_normal_action').read()[0]

    @api.multi
    def action_view(self):
        action = self.action_view_base()
        form = self.env.ref('product.product_normal_form_view')
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            tree = self.env.ref('product.product_product_tree_view')
            action['domain'] = [('id', 'in', self.ids)]
            action['views'] = [(tree.id, 'tree'), (form.id, 'form')]
            action['view_mode'] = 'tree,form'
        else:
            action['views'] = [(form.id, 'form')]
            action['view_mode'] = 'form'
            action['res_id'] = self.ids[0]
        return action

    @api.multi
    def action_view_template(self):
        action = self.mapped('product_tmpl_id').action_view()
        return action
