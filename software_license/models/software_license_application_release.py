# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

import semver

from odoo import _, api, fields, models


class SoftwareLicenseApplicationRelease(models.Model):
    _name = 'software.license.application.release'
    _description = 'License Application Release'
    _order = 'version_major, version_minor, version_patch'
    _desc_order = 'version_major desc, version_minor desc, version_patch desc'
    _rec_name = 'version'

    @api.model
    def _get_default_version(self):
        latest_release_ids = self.search([], order=self._desc_order, limit=1)
        if latest_release_ids:
            ver = semver.VersionInfo.parse(latest_release_ids.version)
            return str(ver.bump_major())
        else:
            return "1.0.0"

    def _get_default_content_items(self, name="item", count=1):
        items = []
        for i in range(count):
            items.append("<li><p>%s %d</p></li>" % (name, i + 1))
        return "<ul>%s</ul>" % ''.join(items)

    @api.model
    def _get_default_content(self):
        default_titles = [
            (_("What's New"), _('new')),
            (_("Fixes"), _('fix')),
            (_("Known Issues"), _('issue')),
        ]
        content = []
        for title, item_name in default_titles:
            content.append(
                "<h2>%s</h2>%s" % (
                    title,
                    self._get_default_content_items(item_name, 3),
                )
            )
        return ''.join(content)

    application_id = fields.Many2one(
        comodel_name='software.license.application',
        string="Application",
        required=True,
    )
    version = fields.Char(
        string="Version",
        help="Version numbering using semver https://semver.org",
        default=_get_default_version,
        required=True,
    )
    version_major = fields.Integer(
        compute="_compute_version_info",
        store=True,
    )
    version_minor = fields.Integer(
        compute="_compute_version_info",
        store=True,
    )
    version_patch = fields.Integer(
        compute="_compute_version_info",
        store=True,
    )
    date = fields.Date(
        string="Date",
        help="Release's Date",
        required=True,
        default=fields.Date.context_today,
    )
    content = fields.Html(
        string='Release Notes',
        translate=False,
        sanitize=False,
        default=_get_default_content,
    )
    url = fields.Char(string='Download URL', )

    @api.depends("version")
    def _compute_version_info(self):
        for rec in self:
            ver = semver.VersionInfo.parse(rec.version)
            rec.version_major = ver.major
            rec.version_minor = ver.minor
            rec.version_patch = ver.patch

    # active = fields.Boolean(
    #     'Active',
    #     default=True,
    #     help="If unchecked, it will allow you to hide the application "
    #     "without removing it.",
    # )
    # identifier = fields.Integer(
    #     'Identifier',
    #     required=True,
    #     default=0,
    # )
    # name = fields.Text(
    #     'Application',
    #     required=True,
    # )
    # template_id = fields.Many2one(
    #     comodel_name='software.license',
    #     string='License Template',
    #     help="Select a license that will be used as a template when creating "
    #     "a new license",
    #     domain="[('application_id', '=', id), ('type', '=', 'template')]",
    # )
    # info = fields.Text(
    #     string='Informations',
    #     help="This field is deprecated, use the chatter now.",
    # )
    # product_id = fields.Many2one(
    #     comodel_name='product.product',
    #     string="Related Product",
    #     help="By linking this application to a product, sales informations "
    #     "like description will be used in communications to customers",
    # )

    # def _prepare_license_template_vals(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'template',
    #         'application_id': self.id,
    #     }

    # @api.multi
    # def action_create_license_template(self):
    #     for rec in self:
    #         vals = rec._prepare_license_template_vals()
    #         rec.template_id = self.env['software.license'].with_context(
    #             default_type='template'
    #         ).create(vals)
