# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    note = fields.Text('Internal Notes')

    @api.multi
    def write(self, vals):
        if vals.get('note'):
            self.message_post(
                body=_("Internal notes changed to: {}"
                      ).format(vals.get('note'))
            )
        res = super().write(vals)
        return res