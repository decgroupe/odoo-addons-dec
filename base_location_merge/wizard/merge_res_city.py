# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import fields, models


class MergeResCity(models.TransientModel):
    _inherit = "merge.object.wizard"
    _name = "merge.res.city.wizard"
    _description = "Merge City Wizard"
    _model_merge = "res.city"
    _table_merge = "res_city"

    object_ids = fields.Many2many(
        comodel_name=_model_merge,
        string="City",
    )
    dst_object_id = fields.Many2one(
        comodel_name=_model_merge,
        string="Destination City",
    )

    def _merge(self, object_ids, dst_object=None, extra_checks=True):
        # Before merging cities, we first need to merge same zip by name
        res_city_ids = self.env[self._model_merge].browse(object_ids)
        groups = {}
        for zip_id in res_city_ids.mapped("zip_ids"):
            group_key = (zip_id.name,)
            groups.setdefault(
                group_key,
                {
                    "ref": False,
                    "ids": [],
                },
            )
            if not groups[group_key]["ref"] and zip_id.city_id == dst_object:
                groups[group_key]["ref"] = zip_id
            groups[group_key]["ids"].append(zip_id.id)

        # We have grouped all zips by name so we can now merge them using
        # their own merge wizard. Note that ref is a reference to a zip_id
        # owned by dst_object
        city_zip_wiz = self.env["merge.res.city.zip.wizard"].create({})
        for key, value in groups.items():
            city_zip_wiz._merge(value["ids"], value["ref"])
        city_zip_wiz.unlink()

        # Finally also merge selected cities
        return super()._merge(object_ids, dst_object, extra_checks)
