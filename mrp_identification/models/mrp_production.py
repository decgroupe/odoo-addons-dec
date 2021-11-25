# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import api, models, _

SEARCH_SEPARATOR = ' →'


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if SEARCH_SEPARATOR in name:
            name = name.partition(SEARCH_SEPARATOR)[0]
        names = super(MrpProduction, self.with_context(
            name_search=True
        )).name_search(name=name, args=args, operator=operator, limit=limit)
        return names

    @api.multi
    def name_get(self):
        if self.env.context.get('name_search'):
            return self.name_get_from_search()
        else:
            return super().name_get()

    @api.multi
    @api.depends('name')
    def name_get_from_search(self):
        """ Custom naming to quickly identify a production order
        """
        res = []
        for rec in self:
            identification = ' '.join(rec._get_name_identifications())
            name = '%s%s %s' % (rec.name, SEARCH_SEPARATOR, identification)
            res.append((rec.id, name))
        return res

    @api.multi
    @api.depends('bom_id', 'partner_id', 'partner_zip_id')
    def _get_name_identifications(self):
        self.ensure_one()
        res = []
        if self.bom_id:
            res.append('⚙️ %s' % (self.bom_id.display_name))
        if self.partner_id:
            res.append(
                '%s %s' % (
                    self.partner_id._get_contact_type_emoji(),
                    self.partner_id.display_name
                )
            )
        if self.partner_zip_id:
            res.append('🗺️ %s' % (self.partner_zip_id.display_name))
        return res
