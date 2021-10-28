# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import _, api, fields, models, tools
from odoo.tools import pycompat


class SoftwareLicenseApplication(models.Model):
    _name = 'software.license.application'
    _description = 'License application'
    _order = 'identifier asc, name'

    active = fields.Boolean(
        'Active',
        default=True,
        help="If unchecked, it will allow you to hide the application "
        "without removing it.",
    )
    identifier = fields.Integer(
        'Identifier',
        required=True,
        default=0,
    )
    name = fields.Text(
        'Application',
        required=True,
    )
    template_id = fields.Many2one(
        comodel_name='software.license',
        string='License Template',
        help="Select a license that will be used as a template when creating "
        "a new license",
        domain="[('application_id', '=', id), ('type', '=', 'template')]",
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
        comodel_name='software.license.application.release',
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

    def _prepare_license_template_vals(self):
        self.ensure_one()
        return {
            'type': 'template',
            'application_id': self.id,
        }

    @api.multi
    def action_create_license_template(self):
        for rec in self:
            vals = rec._prepare_license_template_vals()
            rec.template_id = self.env['software.license'].with_context(
                default_type='template'
            ).create(vals)

    @api.depends('attachment_image')
    def _compute_image(self):
        self.ensure_one()
        if self._context.get('bin_size'):
            self.image = self.attachment_image
        else:
            self.image = tools.image_resize_image(
                self.attachment_image, size=(300, 200)
            )

    def _inverse_image(self):
        self.ensure_one()
        value = self.image
        if isinstance(value, pycompat.text_type):
            value = value.encode('ascii')
        self.attachment_image = tools.image_resize_image(value, size=(300, 200))
