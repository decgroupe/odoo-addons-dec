# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2020

from odoo import api, models


class UoM(models.Model):
    _inherit = "uom.uom"
    _name_search_order = "factor desc, name"

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        if not args:
            args = []

        uom_ids = []
        if name:
            positive_operators = ["=", "ilike", "=ilike", "like", "=like"]
            if operator in positive_operators:
                uom_ids = list(
                    self._search(
                        args + [("name", "=ilike", name)],
                        limit=limit,
                        access_rights_uid=name_get_uid,
                        order=self._name_search_order,
                    )
                )

            if not limit or len(uom_ids) < limit:
                limit2 = (limit - len(uom_ids)) if limit else False
                uom2_ids = list(
                    self._search(
                        args
                        + [
                            ("name", "=ilike", name + "%"),
                            ("id", "not in", uom_ids),
                        ],
                        limit=limit2,
                        access_rights_uid=name_get_uid,
                        order=self._name_search_order,
                    )
                )
                uom_ids.extend(uom2_ids)

            if not limit or len(uom_ids) < limit and operator != "=ilike":
                limit3 = (limit - len(uom_ids)) if limit else False
                uom3_ids = list(
                    self._search(
                        args
                        + [
                            ("name", operator, name),
                            ("id", "not in", uom_ids),
                        ],
                        limit=limit3,
                        access_rights_uid=name_get_uid,
                        order=self._name_search_order,
                    )
                )
                uom_ids.extend(uom3_ids)
        else:
            uom_ids = list(
                self._search(
                    args,
                    limit=limit,
                    access_rights_uid=name_get_uid,
                )
            )
        # print(list(self.browse(uom_ids).mapped("name")))
        return uom_ids
