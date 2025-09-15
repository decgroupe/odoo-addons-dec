# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import api, fields, models


class SoftwareApplication(models.Model):
    _inherit = "software.application"

    # Add a new type to set this application as a launcher that can handle other
    # applications as a software library manager
    type = fields.Selection(
        selection_add=[
            (
                "launcher",
                "Launcher",
            )
        ],
        ondelete={"launcher": "set default"},
    )
    application_ids = fields.Many2many(
        comodel_name="software.application",
        relation="software_asset_application_rel",
        column1="launcher_id",
        column2="app_id",
        string="Applications",
        domain=[("type", "=", "inhouse")],
    )
    corner_image = fields.Binary(
        string="Corner Image",
        attachment=True,
    )
    pictogram_image = fields.Binary(
        string="Pictogram Image",
        attachment=True,
    )
    image_ids = fields.One2many(
        comodel_name="software.application.image",
        inverse_name="application_id",
        string="Tooltips",
    )
    is_free = fields.Boolean(
        string="Display as « Free »",
        default=False,
    )
    is_soon = fields.Boolean(
        string="Display as « Soon »",
        default=False,
    )
    need_license = fields.Boolean(
        string="Only visible with a valid license",
        default=False,
        help="Sometimes, an application is specifically developped for a "
        "customer and should not be shared with others. This is the purpose "
        "of this setting: Hide this application until the customer is logged "
        "in with an account with a valid license.",
    )

    @api.model
    def allowed_types_for_resources(self):
        res = super().allowed_types_for_resources()
        res.append("launcher")
        return res

    def write(self, vals):
        if "type" in vals:
            if vals.get("type") == "other":
                vals.update(
                    {
                        "corner_image": False,
                        "pictogram_image": False,
                        "image_ids": [(6, 0, [])],
                    }
                )
        return super().write(vals)

    def _get_launcher_manifest_entry(self, with_tooltips=False):
        self.ensure_one()
        is_tool = False
        tag_tool = self.env.ref("software_application_launcher.tag_tool")
        tags = []
        for tag_id in self.tag_ids:
            if tag_tool and tag_id.id == tag_tool.id:
                is_tool = True
            tags.append(
                {
                    "tag": tag_id.name,
                    "isSecondary": tag_id.color == 0,
                }
            )
        resources = []
        for resource_id in self.resource_ids:
            resources.append(
                {
                    "name": resource_id.name,
                    "identifier": resource_id.identifier,
                }
            )
        releases = []
        for release_id in self.release_ids:
            releases.append(
                {
                    "version": {
                        "string": release_id.version,
                        "major": release_id.version_major,
                        "minor": release_id.version_minor,
                        "patch": release_id.version_patch,
                        "prerelease": release_id.version_prerelease,
                        "build": release_id.version_build,
                    },
                    "date": release_id.date,
                    "url": release_id.url,
                }
            )
        tooltip_images = []
        if with_tooltips:
            for image_id in self.image_ids:
                tooltip_images.append(
                    {
                        "name": image_id.name,
                        "image": image_id.resized_image,
                    }
                )
        return {
            "name": self.name,
            "productName": self.product_name,
            "productDescription": self.product_description,
            "identifier": self.identifier,
            "image": self.image,
            "isSoon": self.is_soon,
            "isFree": self.is_free,
            "isTool": is_tool,
            "shopLink": self.website,
            "needLicense": self.need_license,
            "resources": resources,
            "releases": releases,
            "tags": tags,
            "cornerImage": self.corner_image,
            "pictogramImage": self.pictogram_image,
            "tooltipImages": tooltip_images,
        }
