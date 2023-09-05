# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2023

import logging

from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)


class MailActivityTeam(models.AbstractModel):
    _inherit = "mail.activity.team"

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        string="Image",
        attachment=True,
        help="This field holds the image used for this team, limited " "to 1024x1024px",
    )
    image_medium = fields.Binary(
        string="Medium-sized image",
        attachment=True,
        help="Medium-sized image of this team. It is automatically "
        "resized as a 128x128px image, with aspect ratio preserved. "
        "Use this field in form views or some kanban views.",
    )
    image_small = fields.Binary(
        string="Small-sized image",
        attachment=True,
        help="Small-sized image of this team. It is automatically "
        "resized as a 64x64px image, with aspect ratio preserved. "
        "Use this field anywhere a small image is required.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            tools.image_resize_images(vals)
        return super(MailActivityTeam, self).create(vals_list)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(MailActivityTeam, self).write(vals)
