# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SoftwareTag(models.Model):
    _name = "software.tag"
    _description = "Software Tag"

    name = fields.Char(required=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]

    def unlink(self):
        if self.env.ref(
            "software_application_launcher.tag_tool"
        ).id in self.ids:
            raise UserError(_("This tag cannot be removed"))
        return super().unlink()
