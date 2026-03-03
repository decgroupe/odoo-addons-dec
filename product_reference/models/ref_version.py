# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class RefVersion(models.Model):
    _name = "ref.version"
    _description = "Reference version"

    @api.model
    def _default_version(self):
        res = 1
        if "version_ids" in self.env.context:
            for rec_id in self.env.context.get("version_ids"):
                if isinstance(rec_id, int):
                    version_id = self.browse(rec_id)
                    if version_id.version > res:
                        res = version_id.version
        return res

    name = fields.Char(
        "Modification name",
        size=128,
        required=True,
    )
    version = fields.Integer(
        string="Version",
        default=lambda self: self._default_version(),
        required=True,
    )
    datetime = fields.Datetime(
        string="Modification date",
        default=lambda self: self._default_datetime(),
    )
    author_id = fields.Many2one(
        comodel_name="res.users",
        string="Author",
        default=lambda self: self.env.user,
    )
    reference_id = fields.Many2one(
        comodel_name="ref.reference",
        string="Reference",
    )

    def _default_datetime(self):
        return fields.Datetime.now()
