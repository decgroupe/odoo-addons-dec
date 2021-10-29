# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import fields, models, api


class SoftwareApplicationImage(models.Model):
    _name = 'software.application.image'
    _description = 'Software Application Image'

    @api.model
    def _default_name(self):
        res = 0
        if 'image_ids' in self.env.context:
            for o2m in self.env.context.get('image_ids'):
                name = False
                if isinstance(o2m[1], int):
                    rec_id = o2m[1]
                    name = self.browse(rec_id).name
                elif isinstance(o2m[1], str) and isinstance(o2m[2], dict):
                    rec_data = o2m[2]
                    name = rec_data.get('name', False)
                if name:
                    try:
                        image_num = int(name.split('_')[-1])
                        if image_num > res:
                            res = image_num
                    except ValueError:
                        pass
        return "tooltip_%.2d" % (res + 1)

    name = fields.Char(
        string='Name',
        default=_default_name,
        required=True,
    )
    image = fields.Binary(
        'Image',
        attachment=True,
    )
    application_id = fields.Many2one(
        comodel_name='software.application',
        string='Related Application',
        copy=True,
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        return res
