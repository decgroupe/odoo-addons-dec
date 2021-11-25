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
    @api.depends('name', 'bom_id', 'partner_id', 'partner_zip_id')
    def name_get_from_search(self):
        """ Custom naming to quickly identify a production order
        """
        res = []
        for rec in self:
            name = '%s%s ⚙️ %s' % (
                rec.name, SEARCH_SEPARATOR, rec.bom_id.display_name
            )
            if rec.partner_id:
                if rec.partner_id.is_company:
                    pre = "🏢"
                else:
                    pre = "👷"
                name = ('%s %s %s') % (name, pre, rec.partner_id.display_name)
            if rec.partner_zip_id:
                name = ('%s 🗺️ %s') % (name, rec.partner_zip_id.display_name)
            res.append((rec.id, name))
        return res
