# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import fields, models, api, tools
from odoo.tools import pycompat


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
    resized_image = fields.Binary(
        "Image",
        compute='_compute_image',
        inverse='_inverse_image',
        help="Image of the application (automatically resized)."
    )
    resize_x = fields.Integer(
        string="Resize Width",
        default=225,
    )
    resize_y = fields.Integer(
        string="Resize Height",
        default=150,
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

    @api.depends('image')
    def _compute_image(self):
        for rec in self:
            if rec.env.context.get('bin_size'):
                rec.resized_image = rec.image
            elif rec.resize_x and rec.resize_y:
                rec.resized_image = tools.image_resize_image(
                    rec.image,
                    size=(rec.resize_x, rec.resize_y),
                    avoid_if_small=True
                )
            else:
                rec.resized_image = rec.image

    @api.depends('resize_x', 'resize_y')
    def _inverse_image(self):
        self.ensure_one()
        for rec in self:
            value = rec.resized_image
            if isinstance(value, pycompat.text_type):
                value = value.encode('ascii')
            if rec.resize_x and rec.resize_y:
                rec.image = tools.image_resize_image(
                    value,
                    size=(rec.resize_x, rec.resize_y),
                    avoid_if_small=True
                )
            else:
                rec.image = value
