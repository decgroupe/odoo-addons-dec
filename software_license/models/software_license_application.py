# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import _, api, fields, models


class SoftwareLicenseApplication(models.Model):
    _name = 'software.license.application'
    _description = 'License application'
    _order = 'application_id asc, name'

    application_id = fields.Integer(
        'AppID',
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
    )
    info = fields.Text('Informations')

    def _prepare_licence_template_vals(self):
        self.ensure_one()
        return {
            'active': False,
            'application_id': self.id,
            'serial': _('Template'),
        }

    @api.multi
    def action_create_license_template(self):
        for rec in self:
            vals = rec._prepare_licence_template_vals()
            rec.template_id = self.env['software.license'].create(vals)
