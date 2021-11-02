# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import _, api, fields, models, tools
from odoo.tools import pycompat


class SoftwareApplication(models.Model):
    _name = 'software.application'
    _description = 'Software Application'
    _order = 'identifier asc, name'

    active = fields.Boolean(
        'Active',
        default=True,
        help="If unchecked, it will allow you to hide the application "
        "without removing it.",
    )
    name = fields.Text(
        'Application',
        required=True,
    )
    info = fields.Text(
        string='Informations',
        help="Add details or missing informations",
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Related Product",
        help="By linking this application to a product, sales informations "
        "like description will be used in communications to customers",
    )
    product_name = fields.Char(
        related='product_id.name',
        readonly=False,
    )
    product_description = fields.Text(
        related='product_id.description_sale',
        readonly=False,
    )
    release_ids = fields.One2many(
        comodel_name='software.application.release',
        inverse_name='application_id',
        string="Releases",
    )
    image = fields.Binary(
        "Image",
        compute='_compute_image',
        inverse='_inverse_image',
        help="Image of the application (automatically resized to 300 x 200)."
    )
    attachment_image = fields.Binary(
        "Launcher Image",
        attachment=True,
    )
    tag_ids = fields.Many2many(
        comodel_name='software.tag',
        string='Tags',
    )
    type = fields.Selection(
        selection=[
            ('inhouse', _('In-House Application')),
            ('other', _('Other Application')),
            ('resource', _('Resource')),
        ],
        string='Type',
        default='inhouse',
        required=True
    )

    @api.depends('attachment_image')
    def _compute_image(self):
        for rec in self:
            if rec.env.context.get('bin_size'):
                rec.image = rec.attachment_image
            else:
                rec.image = tools.image_resize_image(
                    rec.attachment_image, size=(300, 200)
                )

    def _inverse_image(self):
        self.ensure_one()
        value = self.image
        if isinstance(value, pycompat.text_type):
            value = value.encode('ascii')
        self.attachment_image = tools.image_resize_image(value, size=(300, 200))

    def write(self, vals):
        if vals.get('type') == 'other':
            vals.update(
                {
                    'identifier': 0,
                    'product_id': False,
                    'template_id': False,
                    'tag_ids': [(6, 0, [])],
                }
            )
        return super().write(vals)
