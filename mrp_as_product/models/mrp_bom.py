# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import api, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.multi
    def action_open_as_product(self):
        action = self.env.ref('product.product_template_action').read()[0]
        form_view = self.env.ref('product.product_template_only_form_view')
        tree_view = self.env.ref('product.product_template_tree_view')
        product_tmpl_ids = self.mapped('product_tmpl_id')

        if len(product_tmpl_ids) == 1:
            action['res_id'] = product_tmpl_ids.ids[0]
            action['view_mode'] = 'form'
            action['views'] = [(form_view.id, 'form')]
        else:
            action['domain'] = [
                ('id', 'in', product_tmpl_ids.ids),
            ]
            action['view_mode'] = 'tree,form'
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]

        action['context'] = {}
        return action
