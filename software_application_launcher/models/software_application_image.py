# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

import base64
import logging

from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)


class SoftwareApplicationImage(models.Model):
    _name = "software.application.image"
    _description = "Software Application Image"

    @api.model
    def _default_name(self):
        """Compute a default name for a new image based on existing siblings."""
        res = 0
        if "image_ids" in self.env.context:
            for o2m in self.env.context.get("image_ids"):
                name = False
                if isinstance(o2m[1], int):
                    rec_id = o2m[1]
                    name = self.browse(rec_id).name
                elif isinstance(o2m[1], str) and isinstance(o2m[2], dict):
                    rec_data = o2m[2]
                    name = rec_data.get("name", False)
                if name:
                    try:
                        image_num = int(name.split("_")[-1])
                        if image_num > res:
                            res = image_num
                    except ValueError:
                        _logger.debug("image name suffix is not a number: %s", name)
        return "tooltip_%.2d" % (res + 1)

    name = fields.Char(
        string="Name",
        default=_default_name,
        required=True,
    )
    image = fields.Binary(
        string="Image",
        attachment=True,
    )
    resized_image = fields.Binary(
        string="Image",
        compute="_compute_image",
        inverse="_inverse_image",
        help="Image of the application (automatically resized).",
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
        comodel_name="software.application",
        string="Related Application",
        copy=True,
    )

    @api.model
    def default_get(self, fields):
        """Return default field values for a new image record."""
        res = super().default_get(fields)
        return res

    @api.depends("image")
    def _compute_image(self):
        """Compute the resized image from the raw image binary."""
        for rec in self:
            if rec.env.context.get("bin_size"):
                rec.resized_image = rec.image
            elif rec.resize_x and rec.resize_y:
                raw = base64.b64decode(rec.image or b"") or False
                if raw:
                    processed = tools.image_process(
                        raw, size=(rec.resize_x, rec.resize_y), quality=30
                    )
                    rec.resized_image = (
                        base64.b64encode(processed) if processed else False
                    )
                else:
                    rec.resized_image = False
            else:
                rec.resized_image = rec.image

    @api.depends("resize_x", "resize_y")
    def _inverse_image(self):
        """Store the original image from the resized image value."""
        self.ensure_one()
        for rec in self:
            raw = base64.b64decode(rec.resized_image or b"") or False
            if rec.resize_x and rec.resize_y and raw:
                processed = tools.image_process(raw, size=(rec.resize_x, rec.resize_y))
                rec.image = base64.b64encode(processed) if processed else False
            else:
                rec.image = rec.resized_image
