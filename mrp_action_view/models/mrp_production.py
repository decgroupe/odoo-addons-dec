# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def action_view_base(self):
        return self.env.ref('mrp.mrp_production_action').read()[0]

    @api.multi
    def action_view(self):
        action = self.action_view_base()
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            action['domain'] = [('id', 'in', self.ids)]
        else:
            form = self.env.ref('mrp.mrp_production_form_view')
            action['views'] = [(form.id, 'form')]
            action['res_id'] = self.ids[0]
        return action
