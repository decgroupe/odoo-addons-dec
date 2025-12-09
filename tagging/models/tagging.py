# Copyright (C) DEC SARL, Inc - All Rights Reserved.

import string
import unicodedata

from odoo import _, api, fields, models

SEPARATOR = "-"
SAFE_CHARS = string.ascii_letters + string.digits + SEPARATOR


def unaccent(txt):
    nfkd_form = unicodedata.normalize("NFKD", txt)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


class TaggingTag(models.Model):
    _name = "tagging.tags"
    _description = "Tag"
    _order = "name"

    name = fields.Char(string="Tag", required=True)
    color = fields.Integer()
    description = fields.Char(
        string="Text",
        help="Full text description of the tag",
    )
    notes = fields.Text()
    active = fields.Boolean(default=True)
    related_tags_ids = fields.Many2many(
        comodel_name="tagging.tags",
        relation="tagging_related_tags",
        column1="tag_id",
        column2="related_tag_id",
        string="Related Tags",
    )

    _sql_constraints = [
        (
            "tagging_tags_name_unique",
            "unique (name)",
            "The tag names must be unique!",
        ),
    ]

    def _format_name(self, value):
        if value:
            value = unaccent(value.strip().lower())
            value = value.replace(" ", SEPARATOR)

            char_previous = ""
            char_index = 0
            for char_current in value:
                char_index = char_index + 1
                if char_current == SEPARATOR and char_previous == SEPARATOR:
                    value = value[: char_index - 1] + value[char_index:]
                    char_index = char_index - 1

                char_previous = char_current

            value = "".join([char if char in SAFE_CHARS else "" for char in value])
        return value

    @api.onchange("name")
    def _onchange_tag_name(self):
        self.name = self._format_name(self.name)

    @api.onchange("description")
    def _onchange_tag_description(self):
        self.name = self._format_name(self.description)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "name" in vals:
                vals["name"] = self._format_name(vals["name"])
        res_ids = super().create(vals_list)
        return res_ids

    def write(self, vals):
        if "name" in vals:
            vals["name"] = self._format_name(vals["name"])
        return super().write(vals)
