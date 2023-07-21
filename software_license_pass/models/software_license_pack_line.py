# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import fields, models


class SoftwareLicensePackLine(models.Model):
    _name = "software.license.pack.line"
    _description = "Application Pack Line"

    pack_id = fields.Many2one(
        comodel_name="software.license.pack",
        string="Pack",
        ondelete="cascade",
        index=True,
        required=True,
    )
    application_id = fields.Many2one(
        comodel_name="software.application",
        string="Application",
        index=True,
        required=True,
        ondelete="cascade",
    )
    license_template_id = fields.Many2one(
        comodel_name="software.license",
        string="License Template",
        index=True,
        required=False,
        ondelete="cascade",
        domain="[('application_id', '=', application_id), \
                ('type', '=', 'template'),]",
    )
    feature_ids = fields.One2many(
        comodel_name="software.license.feature",
        related="license_template_id.feature_ids",
        readonly=False,
    )

    _sql_constraints = [
        (
            "app_uniq",
            "unique(pack_id, application_id)",
            "An application must appear only once in a pack!",
        ),
    ]
