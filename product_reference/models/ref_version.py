# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models, api


class RefVersion(models.Model):
    _name = 'ref.version'
    _description = 'Reference version'

    @api.model
    def _default_version(self):
        res = 1
        if 'version_ids' in self.env.context:
            for o2m in self.env.context.get('version_ids'):
                if isinstance(o2m[1], int):
                    rec_id = o2m[1]
                    version_id = self.browse(rec_id)
                    if version_id.version > res:
                        res = version_id.version
                elif isinstance(o2m[1], str) and isinstance(o2m[2], dict):
                    rec_data = o2m[2]
                    if rec_data.get('version', 0) > res:
                        res = rec_data.get('version')
        return res

    name = fields.Char(
        'Modification name',
        size=128,
        required=True,
    )
    version = fields.Integer(
        'Version',
        default=_default_version,
        required=True,
    )
    datetime = fields.Datetime(
        'Modification date',
        default=fields.Datetime.now,
    )
    author_id = fields.Many2one(
        'res.users',
        'Author',
        default=lambda self: self.env.user,
    )
    reference_id = fields.Many2one(
        'ref.reference',
        'Reference',
    )
