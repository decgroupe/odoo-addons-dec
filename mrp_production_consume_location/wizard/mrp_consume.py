# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

from odoo import api, fields, models, _


class MrpConsumeLine(models.TransientModel):
    _inherit = 'mrp.consume.line'

    product_location = fields.Char(compute='_compute_product_location')
    inventory_activity_id = fields.Many2one('mail.activity')

    @api.depends(
        'product_id', 'product_id.loc_rack', 'product_id.loc_row',
        'product_id.loc_case'
    )
    def _compute_product_location(self):
        for line in self:

            def try_append_loc(location, loc):
                if loc:
                    location.append(loc)

            location = []
            try_append_loc(location, line.product_id.loc_rack)
            try_append_loc(location, line.product_id.loc_row)
            try_append_loc(location, line.product_id.loc_case)
            line.product_location = ' . '.join(location)

    @api.multi
    def action_create_inventory_activity(self):
        self.ensure_one()
        # If the user deleted todo activity type.
        try:
            activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        except:
            activity_type_id = False
        vals = {
            'activity_type_id': activity_type_id,
            'summary': _('Requires inventory'),
            'res_id': self.product_id.product_tmpl_id.id,
            'res_model_id': self.env.ref('product.model_product_template').id,
        }
        self.inventory_activity_id = self.env['mail.activity'].create(vals)
        return self.product_produce_id._reopen()
