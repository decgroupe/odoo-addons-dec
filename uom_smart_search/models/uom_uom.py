# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2020

from odoo import api, models


class UoM(models.Model):
    _inherit = 'uom.uom'

    @api.model
    def _name_search(
        self, name, args=None, operator='ilike', limit=100, name_get_uid=None
    ):
        if not args:
            args = []

        uom_ids = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            if operator in positive_operators:
                uom_ids = list(self._search(
                    args + [('name', '=ilike', name)],
                    limit=limit,
                    access_rights_uid=name_get_uid,
                ))

            if not limit or len(uom_ids) < limit:
                limit2 = (limit - len(uom_ids)) if limit else False
                uom2_ids = list(self._search(
                    args + [
                        ('name', '=ilike', name + '%'),
                        ('id', 'not in', uom_ids),
                    ],
                    limit=limit2,
                    access_rights_uid=name_get_uid,
                ))
                uom_ids.extend(uom2_ids)

            if not limit or len(uom_ids) < limit:
                limit3 = (limit - len(uom_ids)) if limit else False
                uom3_ids = list(self._search(
                    args + [
                        ('name', operator, name),
                        ('id', 'not in', uom_ids),
                    ],
                    limit=limit3,
                    access_rights_uid=name_get_uid,
                ))
                uom_ids.extend(uom3_ids)
        else:
            uom_ids = list(self._search(
                args,
                limit=limit,
                access_rights_uid=name_get_uid,
            ))

        return uom_ids
