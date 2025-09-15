# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SoftwareApplication(models.Model):
    _name = "software.application"
    _description = "Software Application"
    _order = "name"

    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide the application "
        "without removing it.",
    )
    name = fields.Text(
        string="Application",
        required=True,
    )
    info = fields.Text(
        string="Informations",
        help="Add details or missing informations",
    )
    website = fields.Char(
        string="Website",
        help="Website of the application",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Related Product",
        help="By linking this application to a product, sales informations "
        "like description will be used in communications to customers",
    )
    product_name = fields.Char(
        related="product_id.name",
        readonly=False,
    )
    product_description = fields.Text(
        related="product_id.description_sale",
        readonly=False,
    )
    release_ids = fields.One2many(
        comodel_name="software.application.release",
        inverse_name="application_id",
        string="Releases",
    )
    image = fields.Image(
        string="Image",
        related="attachment_image",
        max_width=320,
        max_height=240,
        store=True,
        help="Thumbnail image of the application (resized to 320x240).",
    )
    attachment_image = fields.Image(
        string="Launcher Image",
        help="Technical field used to store the image in the database (real size)",
    )
    tag_ids = fields.Many2many(
        comodel_name="software.tag",
        string="Tags",
    )
    type = fields.Selection(
        selection=[
            ("inhouse", "In-House Application"),
            ("other", "Other Application"),
            ("resource", "Resource"),
        ],
        string="Type",
        default="inhouse",
        required=True,
    )
    resource_ids = fields.Many2many(
        comodel_name="software.application",
        relation="software_asset_resource_rel",
        column1="app_id",
        column2="res_id",
        string="Resources",
        domain=[("type", "=", "resource")],
    )

    @api.model
    def allowed_types_for_resources(self):
        return ["inhouse"]

    def write(self, vals):
        if "type" in vals:
            if vals.get("type") == "other":
                vals.update(
                    {
                        "product_id": False,
                        "tag_ids": [(6, 0, [])],
                    }
                )
            if vals.get("type") not in self.allowed_types_for_resources():
                vals.update(
                    {
                        "resource_ids": [(6, 0, [])],
                    }
                )
        return super().write(vals)
