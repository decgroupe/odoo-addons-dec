# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SoftwareLicense(models.Model):
    _inherit = 'software.license'

    pass_id = fields.Many2one(
        comodel_name='software.license.pass',
        string='Pass',
    )
    pack_id = fields.Many2one(
        comodel_name='software.license.pack',
        related='pass_id.pack_id',
    )
    pack_line_id = fields.Many2one(
        comodel_name='software.license.pack.line',
        string="Pack Line",
        help="Line of the pack used to generate this license",
    )

    PASS_LOCKED_FIELDS = [
        'partner_id',
        'max_allowed_hardware',
        'expiration_date',
    ]

    @api.multi
    def write(self, vals):
        if not self.env.context.get('override_from_pass'):
            locked_fields = []
            for key in list(vals):
                if (key in self.PASS_LOCKED_FIELDS):
                    locked_fields.append(key)
            if locked_fields:
                raise UserError(
                    _(
                        "It is forbidden to update these license's fields when owned by a pass:\n{}"
                    ).format('\n'.join(locked_fields))
                )
        return super().write(vals)

    @api.multi
    def unlink(self):
        license_id_from_pass = self.filtered('pass_id')
        if license_id_from_pass:
            pass_names = [
                x.name for x in license_id_from_pass.mapped('pass_id')
            ]
            raise UserError(
                _('It is forbidden to delete a license own by a pass:\n{}'
                 ).format('\n'.join(pass_names))
            )
        return super().unlink()

    def _name_get(self):
        res = super()._name_get()
        if self.pack_id:
            pack_name = self.pack_id.display_name
            res = _('%s (%s for %s)') % (res, self.serial, pack_name)
        return res

    @api.multi
    def _get_template_id(self):
        template_id = super()._get_template_id()
        # If this license is own by a pass, then use the original license
        # template when resyncing features
        if self.pack_line_id:
            return self.pack_line_id.license_template_id
        return template_id

    @api.multi
    @api.depends('pass_id', 'pass_id.serial')
    def _compute_activation_identifier(self):
        super()._compute_activation_identifier()
        for rec in self.filtered('pass_id'):
            rec.activation_identifier = rec.pass_id.serial

    def _prepare_export_vals(self, include_activation_identifier=True):
        res = super()._prepare_export_vals(include_activation_identifier)
        res.update({
            'pack': self.pack_id.name,
            'pass': self.pass_id.name,
        })
        return res
