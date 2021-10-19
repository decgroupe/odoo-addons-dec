# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import _, api, fields, models


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
    info = fields.Text('Informations')

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
