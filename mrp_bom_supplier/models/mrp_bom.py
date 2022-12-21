# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if args is None:
            args = []

        bom_ids = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            if operator in positive_operators:
                bom_ids = list(self._search(
                    args + [('code', '=ilike', name)],
                    limit=limit,
                ))

            if not limit or len(bom_ids) < limit:
                limit2 = (limit - len(bom_ids)) if limit else False
                bom2_ids = list(self._search(
                    args + [
                        ('code', '=ilike', name + '%'),
                        ('id', 'not in', bom_ids),
                    ],
                    limit=limit2,
                ))
                bom_ids.extend(bom2_ids)

            if not limit or len(bom_ids) < limit:
                limit3 = (limit - len(bom_ids)) if limit else False
                bom3_ids = list(self._search(
                    args + [
                        ('code', operator, name),
                        ('id', 'not in', bom_ids),
                    ],
                    limit=limit3,
                ))
                bom_ids.extend(bom3_ids)
        else:
            bom_ids = list(self._search(
                args,
                limit=limit,
            ))

        return self.browse(bom_ids).name_get()
